from django.contrib.auth.models import AbstractUser, User
from django.db import models

# Create your models here.
from django.db import models

class Card(models.Model):
    card_number = models.CharField(max_length=16)
    cvv_number = models.CharField(max_length=3)
    expiration_date = models.DateField()

class LinkedAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pin = models.CharField(max_length=6)
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.bank_name} - {self.account_number}'

