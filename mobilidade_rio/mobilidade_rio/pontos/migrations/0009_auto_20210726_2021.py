# Generated by Django 3.1.13 on 2021-07-26 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pontos', '0008_auto_20210726_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trip',
            name='version',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
