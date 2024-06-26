# Generated by Django 4.2.11 on 2024-04-08 06:34

from django.db import migrations, models
import django.db.models.deletion
import django_lifecycle.mixins
import pgtrigger.compiler
import pgtrigger.migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(verbose_name='datetime')),
            ],
            options={
                'verbose_name': 'match',
                'verbose_name_plural': 'matches',
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Stadium',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='name')),
                ('description', models.TextField(verbose_name='description')),
                ('logo', models.ImageField(default='', upload_to='', verbose_name='logo')),
                ('capacity', models.PositiveIntegerField(verbose_name='capacity')),
            ],
            options={
                'verbose_name': 'stadium',
                'verbose_name_plural': 'stadiums',
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, verbose_name='name')),
            ],
            options={
                'verbose_name': 'team',
                'verbose_name_plural': 'teams',
            },
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(verbose_name='number')),
                ('is_reserved', models.BooleanField(default=False, verbose_name='is reserved?')),
                ('full_name', models.CharField(default='', verbose_name='full name')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stadium_management.match', verbose_name='match')),
            ],
            options={
                'verbose_name': 'seat',
                'verbose_name_plural': 'seats',
            },
        ),
        migrations.AddField(
            model_name='match',
            name='guest_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guest_match', to='stadium_management.team', verbose_name='guest team'),
        ),
        migrations.AddField(
            model_name='match',
            name='host_team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='host_match', to='stadium_management.team', verbose_name='host team'),
        ),
        migrations.AddField(
            model_name='match',
            name='stadium',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stadium_management.stadium', verbose_name='stadium'),
        ),
        migrations.AddConstraint(
            model_name='seat',
            constraint=models.UniqueConstraint(fields=('number', 'match'), name='match_seats_number_are_unique'),
        ),
        migrations.AddConstraint(
            model_name='seat',
            constraint=models.CheckConstraint(check=models.Q(('is_reserved', True), models.Q(('full_name', ''), _negated=True), ('full_name', ''), ('is_reserved', False)), name='reserved_seats_must_have_full_name'),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name='seat',
            trigger=pgtrigger.compiler.Trigger(name='protect_reserved_seats_from_update_and_delete', sql=pgtrigger.compiler.UpsertTriggerSql(condition='WHEN (OLD."is_reserved")', func="RAISE EXCEPTION 'pgtrigger: Cannot delete or update rows from % table', TG_TABLE_NAME;", hash='d954a9a66bbddb6a70bdbb74f1a7420daa7f3b49', operation='DELETE OR UPDATE', pgid='pgtrigger_protect_reserved_seats_from_update_and_delete_c2061', table='stadium_management_seat', when='BEFORE')),
        ),
    ]
