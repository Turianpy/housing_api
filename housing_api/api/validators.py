import re

from django.contrib.auth import get_user_model
from rest_framework.validators import ValidationError

User = get_user_model()


def validate_username(username):
    if username.casefold() == 'me':
        raise ValidationError('Invalid username')
    if not re.match(r'^\w+$', username):
        raise ValidationError(
            'Username must contain only letters, numbers and underscores'
        )
    return True


def validate_email_exists(email):
    if User.objects.filter(email=email).exists():
        raise ValidationError('Email unavailable')
    return True


def validate_username_exists(username):
    if User.objects.filter(username=username).exists():
        raise ValidationError('Username unavailable')
    return True


def validate_email_and_username_exist(email, username):
    return validate_email_exists(email) and validate_username_exists(username)
