from rest_framework import serializers
from account.models import LinkedAccount, User
from ewallet.models import Transaction, Wallet


class LinkedAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkedAccount
        fields = ['user', 'account_number', 'bank_name', 'balance']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['account', 'amount', 'transaction_type']


class RegisterSerializer(serializers.ModelSerializer):
    model = User
    fields = ['username', 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['account', 'amount', 'transaction_type']


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkedAccount
        fields = ['account_number', 'amount', 'pin']


    def withdraw_amount(self, amount, balance, pin):
        if balance > 0 and amount > 0 and pin == LinkedAccount.pin:
            balance =- amount
        else:
            raise ValueError("Insufficient funds")

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['wallet_id', 'user_account']