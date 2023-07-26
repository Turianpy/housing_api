# Generated by Django 4.2.3 on 2023-07-24 19:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='property',
            old_name='floor',
            new_name='floor_number',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='address',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='property',
            old_name='floors',
            new_name='total_floors',
        ),
        migrations.RemoveField(
            model_name='property',
            name='area',
        ),
        migrations.RemoveField(
            model_name='property',
            name='city',
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('zipcode', models.IntegerField()),
                ('country', models.CharField(max_length=255)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('property', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='location', to='properties.property')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
                ('main', models.BooleanField(default=False)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='properties.property')),
            ],
        ),
    ]