# Generated by Django 3.1.14 on 2022-12-07 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pontos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stoptimes',
            name='stop_sequence',
            field=models.CharField(max_length=500),
        ),
    ]
