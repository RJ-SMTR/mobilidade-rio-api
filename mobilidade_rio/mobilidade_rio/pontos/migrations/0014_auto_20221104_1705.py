# Generated by Django 3.1.14 on 2022-11-04 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pontos', '0013_auto_20211108_2202'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Sequence',
            new_name='Stop_times',
        ),
        migrations.RenameField(
            model_name='agency',
            old_name='id',
            new_name='agency_id',
        ),
        migrations.RenameField(
            model_name='qrcode',
            old_name='code',
            new_name='stop_code',
        ),
        migrations.RenameField(
            model_name='route',
            old_name='agency',
            new_name='agency_id',
        ),
        migrations.RenameField(
            model_name='route',
            old_name='id',
            new_name='route_id',
        ),
        migrations.RenameField(
            model_name='route',
            old_name='vista',
            new_name='route_long_name',
        ),
        migrations.RenameField(
            model_name='route',
            old_name='short_name',
            new_name='route_short_name',
        ),
        migrations.RenameField(
            model_name='stop',
            old_name='id',
            new_name='stop_id',
        ),
        migrations.RenameField(
            model_name='stop',
            old_name='latitude',
            new_name='stop_lat',
        ),
        migrations.RenameField(
            model_name='stop',
            old_name='longitude',
            new_name='stop_lon',
        ),
        migrations.RenameField(
            model_name='stop',
            old_name='name',
            new_name='stop_name',
        ),
        migrations.RenameField(
            model_name='stop_times',
            old_name='stop',
            new_name='stop_id',
        ),
        migrations.RenameField(
            model_name='stop_times',
            old_name='trip',
            new_name='trip_id',
        ),
        migrations.RenameField(
            model_name='trip',
            old_name='direction',
            new_name='direction_id',
        ),
        migrations.RenameField(
            model_name='trip',
            old_name='route',
            new_name='route_id',
        ),
        migrations.RenameField(
            model_name='trip',
            old_name='id',
            new_name='trip_id',
        ),
        migrations.RemoveField(
            model_name='agency',
            name='name',
        ),
        migrations.RemoveField(
            model_name='route',
            name='linha',
        ),
        migrations.RemoveField(
            model_name='route',
            name='mode',
        ),
        migrations.RemoveField(
            model_name='stop',
            name='address',
        ),
        migrations.RemoveField(
            model_name='stop',
            name='mode',
        ),
        migrations.RemoveField(
            model_name='trip',
            name='headsign',
        ),
        migrations.RemoveField(
            model_name='trip',
            name='version',
        ),
        migrations.RemoveField(
            model_name='trip',
            name='via',
        ),
        migrations.AddField(
            model_name='agency',
            name='agency_name',
            field=models.CharField(default=str, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='route',
            name='route_type',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='trip',
            name='trip_headsign',
            field=models.CharField(default=str, max_length=250),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Linha',
        ),
        migrations.DeleteModel(
            name='Mode',
        ),
    ]
