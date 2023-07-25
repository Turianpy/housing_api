# Generated by Django 4.2.3 on 2023-07-25 14:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0004_property_listed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rentdetails',
            name='property',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rent_details', to='properties.property'),
        ),
    ]
