import factory
from faker import Faker
from users.models import User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda x: fake.name())
    email = factory.LazyAttribute(lambda x: fake.email())
    password = factory.LazyAttribute(lambda x: fake.password())
    role = User.USER
    phone_number = factory.LazyAttribute(lambda x: fake.phone_number())
    first_name = factory.LazyAttribute(lambda x: fake.first_name())
    last_name = factory.LazyAttribute(lambda x: fake.last_name())
