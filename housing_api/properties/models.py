from django.contrib.postgres.fields import ArrayField
from django.db import models
from djmoney.models.fields import MoneyField

from .utils import FEATURES_LIST

PROPERTY_TYPES = (
    ('house', 'House'),
    ('apartment', 'Apartment'),
    ('condo', 'Condo'),
    ('townhouse', 'Townhouse'),
    ('land', 'Land'),
    ('other', 'Other')
)
UTILITY_OPTIONS = (
    ('included', 'Included'),
    ('paid by tenant', 'Paid by tenant'),
)


class Property(models.Model):
    listed = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    description = models.TextField()
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    for_sale = models.BooleanField(default=True)
    owner = models.ForeignKey(
        'users.User',
        related_name='properties',
        on_delete=models.CASCADE
    )
    agent = models.ForeignKey(
        'users.User',
        related_name='properties_as_agent',
        on_delete=models.CASCADE,
        null=True
    )
    built = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPES,
        default='apartment'
    )
    features = ArrayField(
        models.CharField(max_length=255, choices=FEATURES_LIST),
        blank=True,
        null=True
    )
    total_floors = models.IntegerField(blank=True, null=True)
    floor_number = models.IntegerField(blank=True, null=True)


class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    property = models.ForeignKey(
        Property,
        related_name='images',
        on_delete=models.CASCADE
    )
    main = models.BooleanField(default=False)


class RentDetails(models.Model):
    UTILITY_OPTIONS = (
        ('included', 'Included'),
        ('paid by tenant', 'Paid by tenant'),
    )

    property = models.OneToOneField(
        Property,
        related_name='rent_details',
        on_delete=models.CASCADE
    )
    rent_price = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='USD'
        )
    min_rent_time = models.IntegerField(blank=True, null=True)
    available_from = models.DateField(blank=True, null=True)
    available_to = models.DateField(blank=True, null=True)
    utilities = models.CharField(
        max_length=20,
        choices=UTILITY_OPTIONS,
        default='paid by tenant'
    )
    deposit_amount = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency='USD'
    )


class Location(models.Model):
    property = models.OneToOneField(
        Property,
        related_name='location',
        on_delete=models.CASCADE
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    zipcode = models.IntegerField()
    country = models.CharField(max_length=255)
