# Generated by Django 3.1.14 on 2022-11-04 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pontos', '0014_auto_20221104_1705'),
    ]

    operations = [
        migrations.RenameField(
            model_name='qrcode',
            old_name='stop',
            new_name='stop_id',
        ),
        migrations.AlterField(
            model_name='agency',
            name='agency_id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]