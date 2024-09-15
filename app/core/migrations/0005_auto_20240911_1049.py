# Generated by Django 3.2.25 on 2024-09-11 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20240911_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='time_minutes',
            field=models.IntegerField(),
        ),
    ]
