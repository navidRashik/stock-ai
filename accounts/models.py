from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UserManager

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'))

ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('user', 'User'))


class User(AbstractUser):
    username = models.CharField(max_length=12, unique=True, blank=True, null=True)
    role = models.CharField(choices=ROLE_CHOICES, max_length=12, error_messages={
        'required': "Role must be provided"
    })
    gender = models.CharField(choices=GENDER_CHOICES, max_length=10, blank=True, null=True, default="")
    email = models.EmailField(unique=True, blank=False,
                              error_messages={
                                  'unique': "A user with that email already exists.",
                              })

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __unicode__(self):
        return self.email

    objects = UserManager()
