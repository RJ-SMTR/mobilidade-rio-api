# Generated by Django 3.1.13 on 2021-07-26 19:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pontos', '0003_route_long_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='route',
            old_name='long_name',
            new_name='vista',
        ),
    ]
