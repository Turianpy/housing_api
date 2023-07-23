from celery import shared_task
from celery.utils.log import get_task_logger

from .utils import send_activation_email, send_reset_password_email

logger = get_task_logger(__name__)


@shared_task(name='send_activation_email')
def send_activation_email_task(username, email, token):
    logger.info(f'Sending activation email to {username} at {email}')
    send_activation_email(username, email, token)
    return 1


@shared_task(name='send_reset_password_email')
def send_reset_password_email_task(username, email, token):
    logger.info(f'Sending reset password email to {username} at {email}')
    send_reset_password_email(username, email, token)
    return 1
