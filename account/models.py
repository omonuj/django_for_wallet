from django.contrib.auth.models import AbstractUser, User
from django.db import models

from django.db import models


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="account")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    linked_cards = models.JSONField(default=list)  # Store linked card details as JSON

    def __str__(self):
        return f"{self.user.username}'s Account"

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.save()


class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cards")
    card_number = models.CharField(max_length=16, unique=True)
    cvv_number = models.CharField(max_length=3)
    expiration_date = models.DateField()

    def __str__(self):
        return f"Card {self.card_number[-4:]}"


class LinkedAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="linked_accounts")
    pin = models.CharField(max_length=6)
    account_number = models.CharField(max_length=20, unique=True)
    bank_name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.bank_name} - {self.account_number}'
