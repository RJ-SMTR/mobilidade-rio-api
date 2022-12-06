# Generated by Django 3.1.14 on 2022-12-06 14:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('agency_id', models.CharField(blank=True, max_length=500, primary_key=True, serialize=False)),
                ('agency_name', models.CharField(max_length=500)),
                ('agency_url', models.URLField(max_length=500)),
                ('agency_timezone', models.CharField(max_length=500)),
                ('agency_lang', models.CharField(blank=True, max_length=500, null=True)),
                ('agency_phone', models.CharField(blank=True, max_length=500, null=True)),
                ('agency_branding_url', models.CharField(blank=True, max_length=500, null=True)),
                ('agency_fare_url', models.CharField(blank=True, max_length=500, null=True)),
                ('agency_email', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('service_id', models.CharField(blank=True, max_length=500, primary_key=True, serialize=False)),
                ('monday', models.IntegerField()),
                ('tuesday', models.IntegerField()),
                ('wednesday', models.IntegerField()),
                ('thursday', models.IntegerField()),
                ('friday', models.IntegerField()),
                ('saturday', models.IntegerField()),
                ('sunday', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='CalendarDates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_id', models.CharField(max_length=500)),
                ('date', models.DateField()),
                ('exception_type', models.CharField(choices=[('1', 'Added service'), ('2', 'Removed service')], max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Frequencies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip_id', models.CharField(blank=True, max_length=500)),
                ('start_time', models.CharField(blank=True, max_length=500, null=True)),
                ('end_time', models.CharField(blank=True, max_length=500, null=True)),
                ('headway_secs', models.CharField(blank=True, max_length=500, null=True)),
                ('exact_times', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Routes',
            fields=[
                ('route_id', models.CharField(blank=True, max_length=500, primary_key=True, serialize=False)),
                ('agency_id', models.CharField(blank=True, max_length=500, null=True)),
                ('route_short_name', models.CharField(blank=True, max_length=500, null=True)),
                ('route_long_name', models.CharField(blank=True, max_length=500, null=True)),
                ('route_desc', models.CharField(blank=True, max_length=500, null=True)),
                ('route_type', models.CharField(blank=True, max_length=500, null=True)),
                ('route_url', models.CharField(blank=True, max_length=500, null=True)),
                ('route_branding_url', models.CharField(blank=True, max_length=500, null=True)),
                ('route_color', models.CharField(blank=True, max_length=500, null=True)),
                ('route_text_color', models.CharField(blank=True, max_length=500, null=True)),
                ('route_sort_order', models.CharField(blank=True, max_length=500, null=True)),
                ('continuous_pickup', models.CharField(blank=True, max_length=500, null=True)),
                ('continuous_drop_off', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Shapes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shape_id', models.CharField(blank=True, max_length=500)),
                ('shape_pt_sequence', models.CharField(blank=True, max_length=500, null=True)),
                ('shape_pt_lat', models.CharField(blank=True, max_length=500, null=True)),
                ('shape_pt_lon', models.CharField(blank=True, max_length=500, null=True)),
                ('shape_dist_traveled', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stops',
            fields=[
                ('stop_id', models.CharField(blank=True, max_length=500, primary_key=True, serialize=False)),
                ('stop_code', models.CharField(blank=True, max_length=500, null=True)),
                ('stop_name', models.CharField(blank=True, max_length=500, null=True)),
                ('stop_desc', models.CharField(blank=True, max_length=500, null=True)),
                ('stop_lat', models.CharField(blank=True, max_length=500, null=True)),
                ('stop_lon', models.CharField(blank=True, max_length=500, null=True)),
                ('zone_id', models.CharField(blank=True, max_length=500, null=True)),
                ('stop_url', models.CharField(blank=True, max_length=500, null=True)),
                ('location_type', models.CharField(blank=True, max_length=500, null=True)),
                ('parent_station', models.CharField(blank=True, max_length=500, null=True)),
                ('stop_timezone', models.CharField(blank=True, max_length=500, null=True)),
                ('wheelchair_boarding', models.CharField(blank=True, max_length=500, null=True)),
                ('platform_code', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Trips',
            fields=[
                ('trip_id', models.CharField(blank=True, max_length=500, primary_key=True, serialize=False)),
                ('service_id', models.CharField(blank=True, max_length=500, null=True)),
                ('trip_headsign', models.CharField(blank=True, max_length=500, null=True)),
                ('trip_short_name', models.CharField(blank=True, max_length=500, null=True)),
                ('direction_id', models.CharField(blank=True, max_length=500, null=True)),
                ('block_id', models.CharField(blank=True, max_length=500, null=True)),
                ('shape_id', models.CharField(blank=True, max_length=500, null=True)),
                ('wheelchair_accessible', models.CharField(blank=True, max_length=500, null=True)),
                ('bikes_allowed', models.CharField(blank=True, max_length=500, null=True)),
                ('route_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pontos.routes')),
            ],
        ),
        migrations.CreateModel(
            name='StopTimes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stop_sequence', models.CharField(blank=True, max_length=500, null=True)),
                ('stop_id', models.CharField(blank=True, max_length=500)),
                ('arrival_time', models.CharField(blank=True, max_length=500, null=True)),
                ('departure_time', models.CharField(blank=True, max_length=500, null=True)),
                ('stop_headsign', models.CharField(blank=True, max_length=500, null=True)),
                ('pickup_type', models.CharField(blank=True, max_length=500, null=True)),
                ('drop_off_type', models.CharField(blank=True, max_length=500, null=True)),
                ('continuous_pickup', models.CharField(blank=True, max_length=500, null=True)),
                ('continuous_drop_off', models.CharField(blank=True, max_length=500, null=True)),
                ('shape_dist_traveled', models.CharField(blank=True, max_length=500, null=True)),
                ('timepoint', models.CharField(blank=True, max_length=500, null=True)),
                ('trip_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trip_id_id', related_query_name='trip_id_id', to='pontos.trips')),
            ],
        ),
        migrations.AddConstraint(
            model_name='shapes',
            constraint=models.UniqueConstraint(fields=('shape_id', 'shape_pt_sequence'), name='shape_sequence_id'),
        ),
        migrations.AddConstraint(
            model_name='frequencies',
            constraint=models.UniqueConstraint(fields=('trip_id', 'start_time'), name='frequency_id'),
        ),
        migrations.AddConstraint(
            model_name='calendardates',
            constraint=models.UniqueConstraint(fields=('service_id', 'date'), name='calendar_date_id'),
        ),
    ]
