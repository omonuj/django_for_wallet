from random import randint
import segno

from django.contrib.auth.models import User
from django.db import models
from util import generate_wallet_number


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=11, unique=True)



class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet_number = models.CharField(max_length=10, unique=True, default=generate_wallet_number, editable=False)
    balance = models.DecimalField(decimal_places=2, default=0.00, max_digits=9)
    wallet_pin = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} {self.wallet_number}"


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10,
                                        choices=[
                                            ('income', 'Income'),
                                            ('expense', 'Expense')
                                        ]
                                        )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.transaction_type} of {self.amount}'

    def deposit(self, amount):
        self.account_amount = amount
        self.save(amount)
        return


class TransactionQRScan(models.Model):
    qrcode = segno.make_qr('')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recipient_account_number = models.IntegerField()
