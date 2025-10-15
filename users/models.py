from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()

    def __str__(self):
        return f'{self.first_name} " " {self.last_name}'
    