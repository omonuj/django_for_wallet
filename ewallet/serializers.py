from rest_framework import serializers

from ewallet.models import Transaction


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['']