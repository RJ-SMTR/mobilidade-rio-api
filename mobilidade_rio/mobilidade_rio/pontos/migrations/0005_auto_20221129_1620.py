# Generated by Django 3.1.14 on 2022-11-29 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pontos', '0004_auto_20221129_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendardates',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='calendardates',
            name='exception_type',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
