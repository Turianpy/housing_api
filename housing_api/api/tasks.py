from celery import shared_task
from celery.utils.log import get_task_logger

from .utils import send_confirmation_code

logger = get_task_logger(__name__)


@shared_task(name='send_conf_code')
def send_confirmation_code_task(username, email, code):
    logger.info(f'Sending confirmation code to {username} at {email}')
    send_confirmation_code(username, email, code)
    return 1
