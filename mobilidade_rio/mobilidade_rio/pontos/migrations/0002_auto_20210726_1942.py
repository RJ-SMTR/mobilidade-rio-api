# Generated by Django 3.1.13 on 2021-07-26 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pontos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='linha',
            name='agency',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pontos.agency'),
        ),
        migrations.AddField(
            model_name='linha',
            name='mode',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pontos.mode'),
        ),
        migrations.AddField(
            model_name='linha',
            name='name',
            field=models.CharField(default='', max_length=150),
        ),
    ]