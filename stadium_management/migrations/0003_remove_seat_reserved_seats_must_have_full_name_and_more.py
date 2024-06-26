# Generated by Django 4.2.11 on 2024-04-08 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stadium_management', '0002_match_seat_price_seat_price_alter_stadium_logo'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='seat',
            name='reserved_seats_must_have_full_name',
        ),
        migrations.AddConstraint(
            model_name='seat',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('is_reserved', True), models.Q(('full_name', ''), _negated=True)), models.Q(('full_name', ''), ('is_reserved', False)), _connector='OR'), name='reserved_seats_must_have_full_name'),
        ),
    ]
