from datetime import timedelta

import pgtrigger
from django.db import models
from django.db.models import CheckConstraint
from django.db.models import Q
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from django_lifecycle import BEFORE_CREATE
from django_lifecycle import LifecycleModel
from django_lifecycle import hook
from rest_framework.exceptions import ValidationError


class Stadium(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=50, unique=True)
    description = models.TextField(verbose_name=_("description"))
    logo = models.ImageField(verbose_name=_("logo"), default="/static/images/logo.png")
    capacity = models.PositiveIntegerField(verbose_name=_("capacity"))

    class Meta:
        verbose_name = _("stadium")
        verbose_name_plural = _("stadiums")

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(verbose_name=_("name"), unique=True)

    class Meta:
        verbose_name = _("team")
        verbose_name_plural = _("teams")

    def __str__(self):
        return self.name


class Match(LifecycleModel):
    # TODO: it's better to put it on the constance package to be configurable
    # from admin panel
    DURATION = timedelta(minutes=120)
    host_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name=_("host team"),
        related_name="host_match",
    )
    guest_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        verbose_name=_("guest team"),
        related_name="guest_match",
    )
    stadium = models.ForeignKey(
        Stadium,
        on_delete=models.CASCADE,
        verbose_name=_("stadium"),
    )
    datetime = models.DateTimeField(verbose_name=_("datetime"))
    seat_price = models.PositiveIntegerField(verbose_name=_("seat price"), default=0)

    class Meta:
        verbose_name = _("match")
        verbose_name_plural = _("matches")

    def __str__(self):
        return (
            f"{self.host_team}:{self.guest_team} at "
            f"{self.datetime} in {self.stadium}"
        )

    @hook(BEFORE_CREATE)
    def validate_stadium_conflict_of_matches(self):
        """It prevents overlapping matches in stadiums"""
        if self.__class__.objects.filter(
            stadium=self.stadium,
            datetime__lte=self.datetime + self.DURATION,
            datetime__gte=self.datetime - self.DURATION,
        ).exists():
            raise ValidationError(
                code=_("stadium_match_conflict"),
                detail=_("This stadium has a match for that date time!"),
            )

    def create_seats(self):
        seats = [
            Seat(number=number, match=self, price=self.seat_price)
            for number in range(1, self.stadium.capacity + 1)
        ]

        Seat.objects.bulk_create(seats)


class Seat(models.Model):
    """Seat is the reservable seats of a match
    - I use full_name instead of user to give
      the ability to reserve seat for anonymous users.
    - As It's possible to have heavy load of reserving seats,
    I use triggers to solve concurrency problems (race condition).
    """

    number = models.PositiveIntegerField(verbose_name=_("number"))
    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name=_("match"))
    is_reserved = models.BooleanField(verbose_name=_("is reserved?"), default=False)
    full_name = models.CharField(verbose_name=_("full name"), default="")
    price = models.PositiveIntegerField(verbose_name=_("price"))

    class Meta:
        verbose_name = _("seat")
        verbose_name_plural = _("seats")
        constraints = [
            UniqueConstraint(
                fields=["number", "match"],
                name="match_seats_number_are_unique",
            ),
            CheckConstraint(
                check=(Q(is_reserved=True) & ~Q(full_name=""))
                | Q(is_reserved=False, full_name=""),
                name="reserved_seats_must_have_full_name",
            ),
        ]
        triggers = [
            pgtrigger.Protect(
                name="protect_reserved_seats_from_update_and_delete",
                operation=pgtrigger.Delete | pgtrigger.Update,
                when=pgtrigger.Before,
                condition=pgtrigger.Q(old__is_reserved=True),
            ),
        ]

    def __str__(self):
        return f"seat {self.number} for match {self.match}"
