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


def validate_email_and_username_exist(email, username):
    email = User.objects.filter(email=email).exists()
    username = User.objects.filter(username=username).exists()

    detail = {}
    if email:
        detail['email'] = 'Email unavailable'
    if username:
        detail['username'] = 'Username unavailable'

    if email or username:
        raise ValidationError(detail)

    return not (email or username)
