import secrets

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import ConfCode


def send_confirmation_code(username, email, code):

    context = {
        'name': username,
        'email': email,
        'conf_code': code,
    }

    email_subject = 'Your konutbul confirmation code'
    email_body = render_to_string(
        'confirmation_code_email.txt',
        context=context
    )

    email = EmailMessage(
        email_subject, email_body,
        settings.DEFAULT_FROM_EMAIL, [email, ],
    )
    return email.send(fail_silently=False)


def generate_conf_code(user):
    return ConfCode.objects.create(
        code=secrets.token_hex(3).upper(), user=user
    )


def get_tokens(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
