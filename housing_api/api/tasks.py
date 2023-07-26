from celery import shared_task
from celery.utils.log import get_task_logger

from .utils import (agent_accept_assignment_email,
                    agent_decline_assignment_email,
                    assign_agent_to_property_link, send_activation_email,
                    send_reset_password_email)

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


@shared_task(name='send_agent_assignment_email')
def send_agent_assignment_email_task(owner, agent, property):
    logger.info(f'Sending agent assignment email to {agent.email}')
    assign_agent_to_property_link(owner, agent, property)
    return 1


@shared_task(name='send_agent_accept_assginment_email')
def send_agent_accept_assginment_email_task(owner, property, agent):
    logger.info(f'Sending agent accept assignment email to {owner.email}')
    agent_accept_assignment_email(owner, agent, property)
    return 1


@shared_task(name='send_agent_decline_assginment_email')
def send_agent_decline_assginment_email_task(owner, property, agent):
    logger.info(f'Sending agent decline assignment email to {owner.email}')
    agent_decline_assignment_email(owner, agent, property)
    return 1
