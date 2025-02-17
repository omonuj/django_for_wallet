from rest_framework import serializers
from account.models import LinkedAccount, User
from ewallet.models import Transaction, Wallet
from django.contrib.auth.hashers import make_password
from wallet.util import generate_wallet_number


class LinkedAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkedAccount
        fields = ['user', 'account_number', 'bank_name', 'balance']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['account', 'amount', 'transaction_type']


class UserSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True, min_length=4, max_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'pin']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        pin = validated_data.pop('pin')
        user = User.objects.create_user(**validated_data)
        Wallet.objects.create(
            user=user,
            balance=0,
            wallet_number=generate_wallet_number(),
            wallet_pin=make_password(pin)
        )
        return user
