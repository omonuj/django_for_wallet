from random import randint
import segno

from django.contrib.auth.models import User
from django.db import models
from wallet.util import generate_wallet_number


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    wallet_number = models.CharField(max_length=10, unique=True, default=generate_wallet_number, editable=False)
    balance = models.DecimalField(decimal_places=2, default=0.00, max_digits=10)
    wallet_pin = models.CharField(max_length=4)

    def __str__(self):
        return f"{self.user} {self.wallet_number}"

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.save()


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=10,
        choices=[
            ('income', 'Income'),
            ('expense', 'Expense')
        ]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.transaction_type} of {self.amount} by {self.wallet.user.username}'


class TransactionQRScan(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="qr_transactions")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recipient_account_number = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        qr = segno.make_qr(f"{self.recipient_account_number}|{self.amount}")
        qr_path = f"qr_codes/{uuid.uuid4().hex}.png"
        qr.save(qr_path, scale=8)
        self.qr_code = qr_path
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Payment {self.amount} to {self.recipient_account_number}"
