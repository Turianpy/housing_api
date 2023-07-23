from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    AGENT = 'agent'
    ROLE_CHOICES = (
        (USER, 'Regular user'),
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (AGENT, 'Real estate agent'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER
    )
    email = models.EmailField(
        unique=True,
        blank=False,
        max_length=254,
    )

    email_verified = models.BooleanField(default=False)
    # ADD PHONE NUMBER VALIDATION LATER !!!!!!!!!!!!!!!!
    phone_number = models.CharField(
        validators=[],
        max_length=20,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_agent(self):
        return self.role == self.AGENT

    @property
    def is_owner(self):
        return self.properties.count() > 0

    class Meta:
        ordering = ('username',)
        verbose_name = 'user'
        verbose_name_plural = 'users'
