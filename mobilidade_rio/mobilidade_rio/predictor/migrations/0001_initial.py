# Generated by Django 3.1.14 on 2022-11-21 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ShapeWithStops',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_short_name', models.CharField(blank=True, max_length=500, null=True)),
                ('trip_id', models.CharField(blank=True, max_length=500)),
                ('stop_sequence', models.CharField(blank=True, max_length=500, null=True)),
                ('stop_id', models.CharField(blank=True, max_length=500)),
                ('shape_dist_traveled', models.CharField(blank=True, max_length=500, null=True)),
                ('shape_id', models.CharField(blank=True, max_length=500)),
                ('shape_pt_sequence', models.CharField(blank=True, max_length=500, null=True)),
                ('shape_pt_lat', models.CharField(blank=True, max_length=500, null=True)),
                ('shape_pt_lon', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
    ]