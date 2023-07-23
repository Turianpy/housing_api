import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def regular_user(django_user_model):
    user = django_user_model.objects.create_user(
        username='test_user',
        email='testuser@random.com'
    )
    user.set_password('test!passwordQSC')
    user.save()
    return user


@pytest.fixture
def regular_user_inactive(regular_user):
    regular_user.is_active = False
    regular_user.save()
    return regular_user


@pytest.fixture
def regular_user_token(regular_user):
    refresh = RefreshToken.for_user(regular_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@pytest.fixture
def regular_user_client(regular_user_token):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION='Bearer ' + regular_user_token['access']
    )
    return client
