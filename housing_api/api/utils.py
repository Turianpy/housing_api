from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken


def send_activation_email(username, email, token):

    activation_link = "http://localhost/api/auth/activate/?token=" + token

    context = {
        "name": username,
        "email": email,
        "activation_link": activation_link
    }

    email_subject = 'Your website_name activation link'
    email_body = render_to_string(
        'activation_link_email.txt',
        context=context
    )

    email = EmailMessage(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL, [email, ],
    )
    return email.send(fail_silently=False)


def generate_activation_token(user):
    payload = {
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(minutes=60),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def get_tokens(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
