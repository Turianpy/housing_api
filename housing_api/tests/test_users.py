import json

import pytest
from django.core import mail

from api.utils import generate_user_token

from .fixtures.user_fixtures import *  # noqa


@pytest.mark.django_db(transaction=True)
class TestUsers:

    users_url = '/api/v1/users/'
    reset_password_url = '/api/v1/users/reset_password/'
    change_password_url = '/api/v1/users/change_password/'

    def test_reset_password_post(self, client, regular_user):
        outbox_before = len(mail.outbox)
        data = {
            'email': regular_user.email,
        }
        response = client.post(self.reset_password_url, data=data)
        assert response.status_code == 200
        assert len(mail.outbox) == outbox_before + 1

    def test_reset_password_post_invalid_email(self, client, regular_user):
        outbox_before = len(mail.outbox)
        data = {
            'email': 'nonexistant@email.com',
        }
        response = client.post(self.reset_password_url, data=data)
        assert response.status_code == 404
        assert len(mail.outbox) == outbox_before

    def test_reset_password_patch(self, client, regular_user):
        data = {
            'new': 'test!passwordQSC2',
            'new_retype': 'test!passwordQSC2'
        }
        token = generate_user_token(regular_user)
        url = self.reset_password_url + '?token=' + token
        response = client.patch(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        regular_user.refresh_from_db()
        assert regular_user.check_password(data['new'])
        assert response.status_code == 200

    def test_reset_password_patch_invalid_token(self, client, regular_user):
        data = {
            'new': 'test!passwordQSC2',
            'new_retype': 'test!passwordQSC2'
        }
        token = generate_user_token(regular_user)
        url = self.reset_password_url + '?token=' + token + 'asdfasdf'
        response = client.patch(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        regular_user.refresh_from_db()
        assert not regular_user.check_password(data['new'])
        assert response.status_code == 400
        assert response.data['error'] == 'Invalid token'

    def test_change_password(self, regular_user_client, regular_user):
        data = {
            'old': 'test!passwordQSC',
            'new': 'test!passwordQSC2',
            'new_retype': 'test!passwordQSC2'
        }
        response = regular_user_client.patch(
            self.change_password_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 200
        assert response.data['message'] == 'Password changed successfully'
        regular_user.refresh_from_db()
        assert regular_user.check_password(data['new'])

    def test_change_password_invalid_old_password(
            self,
            regular_user_client,
            regular_user
    ):
        data = {
            'old': 'test!passwordQSC3',
            'new': 'test!passwordQSC2',
            'new_retype': 'test!passwordQSC2'
        }
        response = regular_user_client.patch(
            self.change_password_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert response.data['old'][0] == 'Incorrect password'
        regular_user.refresh_from_db()
        assert not regular_user.check_password(data['new'])

    def test_change_password_invalid_new_password(
            self,
            regular_user_client,
            regular_user
    ):
        data = {
            'old': 'test!passwordQSC',
            'new': 'test',
            'new_retype': 'test'
        }
        response = regular_user_client.patch(
            self.change_password_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
        regular_user.refresh_from_db()
        assert not regular_user.check_password(data['new'])
        assert response.data['new'][0] == (
            'This password is too short. '
            'It must contain at least 8 characters.'
        )

    def test_change_password_no_match(self, regular_user_client, regular_user):
        data = {
            'old': 'test!passwordQSC',
            'new': 'test!passwordQSC2',
            'new_retype': 'test!passwordQSC3'
        }
        response = regular_user_client.patch(
            self.change_password_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 400
        regular_user.refresh_from_db()
        assert not regular_user.check_password(data['new'])
        assert response.data['new'][0] == 'Passwords do not match'

    def test_users_me(self, regular_user_client, regular_user):
        response = regular_user_client.get(self.users_url + 'me/')
        assert response.status_code == 200
        assert response.data['username'] == regular_user.username
        assert response.data['email'] == regular_user.email
        assert response.data['first_name'] == regular_user.first_name
        assert response.data['last_name'] == regular_user.last_name

    def test_users_me_patch(self, regular_user_client, regular_user):
        data = {
            'first_name': 'new_first_name',
        }
        response = regular_user_client.patch(
            self.users_url + 'me/',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 200
        regular_user.refresh_from_db()
        assert response.data['first_name'] == regular_user.first_name

    def test_users_me_patch_role_forbidden(self, regular_user_client):
        data = {
            'role': 'admin',
        }
        response = regular_user_client.patch(
            self.users_url + 'me/',
            data=json.dumps(data),
            content_type='application/json'
        )
        assert response.status_code == 403
        assert response.data['error'] == 'You cannot change your role here'
