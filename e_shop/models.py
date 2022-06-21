from django.contrib.auth.models import AbstractUser
from django.db import models


class Customer(AbstractUser):
    wallet = models.DecimalField(max_digits=9, decimal_places=2)
