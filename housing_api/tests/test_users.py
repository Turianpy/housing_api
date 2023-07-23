import pytest

from .fixtures.user_fixtures import *  # noqa


@pytest.mark.django_db(transaction=True)
class TestUsers:

    users_url = '/api/v1/users/'
    reset_password_url = '/api/v1/users/reset_password/'
    change_password_url = '/api/v1/users/change_password/'