from __future__ import annotations

import typing

from django.contrib import admin

from stadium_management.forms import MatchAdminAddForm
from stadium_management.models import Match
from stadium_management.models import Seat
from stadium_management.models import Stadium
from stadium_management.models import Team

if typing.TYPE_CHECKING:
    from django.forms import ModelForm
    from django.http import HttpRequest


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    add_form = MatchAdminAddForm
    autocomplete_fields = ["host_team", "guest_team", "stadium"]
    list_display = ["host_team", "guest_team", "stadium", "datetime"]
    search_fields = ["host_team__name", "guest_team__name", "stadium__name"]
    list_filter = ["datetime"]

    def save_model(
        self,
        request: HttpRequest,
        obj: Match,
        form: ModelForm | MatchAdminAddForm,
        change: bool,  # noqa: FBT001
    ):
        """
        After saving the match base on the user input, it will create match seats

        :param request: The HttpRequest object
        :type request: HttpRequest
        :param obj: The match object
        :type obj: Match
        :param form: if it's creating Match the form is MatchAdminAddForm,
            otherwise it's the default form
        :type form: ModelForm | MatchAdminAddForm
        :param change: show operation is update or create
        :type change: bool
        :return: None
        """
        super().save_model(request, obj, form, change)
        if not change:
            does_create_seats = form.cleaned_data.get("does_create_seats", None)
            if does_create_seats is None:
                return
            obj.create_seats()

    def get_form(
        self,
        request: HttpRequest,
        obj: Match | None = None,
        change: bool = False,  # noqa: FBT001, FBT002
        **kwargs,
    ):
        """
        Use special form during match creation

        :param request: The http request object
        :type request: HttpRequest
        :param obj: the match object
        :type obj: Match or None
        :param change: show operation is update or create
        :type change: bool
        :param kwargs: additional keyword arguments
        :type kwargs: dict
        :return: the form instance
        :rtype: ModelForm | MatchAdminAddForm
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ["match", "number", "is_reserved"]
    list_filter = ["is_reserved"]
    search_fields = [
        "full_name",
        "match__host_team__name",
        "match__guest_team__name",
        "match__stadium__name",
    ]
