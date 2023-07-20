import pytest


@pytest.mark.django_db(transaction=True)
class TestAuth:

    def test_test(self):
        assert True
