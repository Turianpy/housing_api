# Generated by Django 4.2.3 on 2023-07-25 15:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0005_alter_rentdetails_property'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rentdetails',
            name='for_rent',
        ),
    ]
