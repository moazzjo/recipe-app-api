# Generated by Django 3.2.25 on 2024-09-20 07:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_ingredientadmin'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='ingredient',
            new_name='ingredients',
        ),
    ]
