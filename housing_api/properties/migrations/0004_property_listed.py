# Generated by Django 4.2.3 on 2023-07-24 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0003_alter_property_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='listed',
            field=models.BooleanField(default=False),
        ),
    ]
