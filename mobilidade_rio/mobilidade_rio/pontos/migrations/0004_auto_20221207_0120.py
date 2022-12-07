# Generated by Django 3.1.14 on 2022-12-07 04:20

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pontos', '0003_auto_20221207_0009'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stops',
            name='location_type',
            field=models.IntegerField(blank=True, choices=[(0, 'stop'), (1, 'station'), (2, 'entrance/exit'), (3, 'generic node'), (4, 'boarding area')], null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(4)]),
        ),
        migrations.AlterField(
            model_name='stops',
            name='parent_station',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pontos.stops'),
        ),
        migrations.AlterField(
            model_name='stops',
            name='stop_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddConstraint(
            model_name='stops',
            constraint=models.CheckConstraint(check=models.Q(models.Q(_negated=True, location_type__in=[2, 3, 4]), ('parent_station__isnull', False), _connector='OR'), name='parent_station_mandatory'),
        ),
        migrations.AddConstraint(
            model_name='stops',
            constraint=models.CheckConstraint(check=models.Q(models.Q(_negated=True, location_type=1), ('parent_station__isnull', True), _connector='OR'), name='parent_station_forbidden'),
        ),
    ]
