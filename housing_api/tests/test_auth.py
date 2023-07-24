import pytest
from django.core import mail

from api.utils import generate_user_token

from .fixtures.user_fixtures import *  # noqa


@pytest.mark.django_db(transaction=True)
class TestAuth:

    signup_url = '/api/v1/auth/signup/'
    activate_url = '/api/v1/auth/activate/'
    token_url = '/api/v1/auth/token/'

    def test_signup(self, client):
        outbox_before = len(mail.outbox)
        data = {
            'username': 'test_user',
            'email': 'testuser@something.com',
            'password': 'test!passwordQSC'
        }
        response = client.post(self.signup_url, data=data)
        assert response.status_code == 201
        assert response.data['username'] == data['username']
        assert response.data['email'] == data['email']
        assert len(mail.outbox) == outbox_before + 1

    def test_signup_with_invalid_email(self, client):
        outbox_before = len(mail.outbox)
        data = {
            'username': 'test_user',
            'email': 'testuser',
            'password': 'test!passwordQSC'
        }
        response = client.post(self.signup_url, data=data)
        assert response.status_code == 400
        assert response.data['email'][0] == 'Enter a valid email address.'
        assert len(mail.outbox) == outbox_before

    def test_signup_with_invalid_password(self, client):
        outbox_before = len(mail.outbox)
        data = {
            'username': 'test_user',
            'email': 'testuser@something.com',
            'password': 'bad'
        }
        response = client.post(self.signup_url, data=data)
        assert response.status_code == 400
        assert response.data['password'][0] == (
            'This password is too short. '
            'It must contain at least 8 characters.'
        )
        assert len(mail.outbox) == outbox_before

    def test_signup_with_invalid_username(self, client):
        outbox_before = len(mail.outbox)
        data = {
            'username': 'me',
            'email': 'testuser',
            'password': 'test!passwordQSC'
        }
        response = client.post(self.signup_url, data=data)
        assert response.status_code == 400
        assert response.data['username'][0] == 'Invalid username'
        assert len(mail.outbox) == outbox_before

    def test_signup_with_existing_credentials(self, client, regular_user):
        outbox_before = len(mail.outbox)
        data = {
            'username': regular_user.username,
            'email': regular_user.email,
            'password': regular_user.password,
        }
        response = client.post(self.signup_url, data=data)
        assert response.status_code == 400
        assert len(mail.outbox) == outbox_before
        assert response.data['email'].code == 'invalid'
        assert response.data['username'].code == 'invalid'
        assert outbox_before == len(mail.outbox)

    def test_activation(self, client, regular_user_inactive):

        token = generate_user_token(regular_user_inactive)
        url = f'{self.activate_url}?token={token}'
        response = client.get(url)
        assert response.status_code == 200
        assert response.data['message'] == 'Account successfully activated'

    def test_activation_invalid_token(self, client):
        url = f'{self.activate_url}?token=invalid_token'
        response = client.get(url)
        assert response.status_code == 400
        assert response.data['error'] == 'Invalid token'

    def test_activation_already_activated(self, regular_user, client):
        token = generate_user_token(regular_user)
        url = f'{self.activate_url}?token={token}'
        response = client.get(url)
        assert response.status_code == 400
        assert response.data['message'] == 'User already activated'

    def test_activation_user_does_not_exist(self, client, user_factory):
        user = user_factory.build()
        token = generate_user_token(user)
        url = f'{self.activate_url}?token={token}'
        response = client.get(url)
        assert response.status_code == 400
        assert response.data['error'] == 'User with given email not found'

    def test_get_token(self, regular_user, client):
        data = {
            'email': regular_user.email,
            'password': 'test!passwordQSC'
        }
        response = client.post(self.token_url, data=data)
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_get_token_with_invalid_credentials(self, regular_user, client):
        data = {
            'email': regular_user.email,
            'password': 'bad_password'
        }
        response = client.post(self.token_url, data=data)
        assert response.status_code == 400
        assert response.data['non_field_errors'][0] == 'Invalid credentials'

        data = {
            'email': 'bad_email',
            'password': 'test!passwordQSC'
        }
        response = client.post(self.token_url, data=data)
        assert response.status_code == 400
        assert response.data['email'][0] == 'Enter a valid email address.'

    def test_get_token_with_inactive_user(self, regular_user_inactive, client):
        data = {
            'email': regular_user_inactive.email,
            'password': 'test!passwordQSC'
        }
        response = client.post(self.token_url, data=data)
        assert response.status_code == 400
        assert response.data['non_field_errors'][0] == 'Account is not active'
