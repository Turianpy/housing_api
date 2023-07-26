from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken


def send_email(subject, body, to):
    email = EmailMessage(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL, [to, ],
    )
    return email.send(fail_silently=False)


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

    send_email(email_subject, email_body, email)


def send_reset_password_email(username, email, token):
    reset_link = "http://localhost/api/auth/reset_password/?token=" + token
    context = {
        "name": username,
        "email": email,
        "reset_link": reset_link
    }

    email_subject = 'Your website_name reset password link'
    email_body = render_to_string(
        'reset_password_link_email.txt',
        context=context
    )

    send_email(email_subject, email_body, email)


def generate_user_token(user):
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


def assign_agent_to_property_link(owner, agent, property):
    link = (
        f"http://localhost/api/properties/{property.id}/"
        f"agent_confirm/?token={generate_user_token(agent)}"
    )
    context = {
        "name": agent.username,
        "email": agent.email,
        "link": link,
        "owner": owner.username
    }
    email_subject = 'The owner of this property has asked you to take it into management as agent'
    email_body = render_to_string(
        'assign_agent_to_property_link_email.txt',
        context=context
    )
    send_email(email_subject, email_body, agent.email)


def agent_accept_assignment_email(owner, agent, property):
    context = {
        "name": owner.username,
        "email": owner.email,
        "agent": agent.username,
        "property": property.title
    }
    email_subject = f'The agent {agent.username} has accepted your request to take this property into management'
    email_body = render_to_string(
        'agent_accept_assignment_email.txt',
        context=context
    )
    send_email(email_subject, email_body, owner.email)


def agent_decline_assignment_email(owner, agent, property):
    context = {
        "name": owner.username,
        "email": owner.email,
        "agent": agent.username,
        "property": property.title
    }
    email_subject = f'The agent {agent.username} has declined your request to take this property into management'
    email_body = render_to_string(
        'agent_decline_assignment_email.txt',
        context=context
    )
    send_email(email_subject, email_body, owner.email)