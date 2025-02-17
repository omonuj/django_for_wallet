from rest_framework import serializers
from ewallet.models import Transaction, Wallet
from account.models import LinkedAccount


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    pin = serializers.CharField(write_only=True, min_length=4, max_length=6)

    def validate(self, data):
        request = self.context["request"]
        wallet = request.user.wallet
        pin = data["pin"]

        if not wallet.check_pin(pin):
            raise serializers.ValidationError("Invalid PIN.")

        if data["amount"] <= 0:
            raise serializers.ValidationError("Deposit amount must be positive.")
        return data


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    pin = serializers.CharField(write_only=True, min_length=4, max_length=6)

    def validate(self, data):
        request = self.context["request"]
        wallet = request.user.wallet
        amount = data["amount"]
        pin = data["pin"]

        if not wallet.check_pin(pin):
            raise serializers.ValidationError("Invalid PIN.")

        if wallet.balance < amount:
            raise serializers.ValidationError("Insufficient funds.")
        data["wallet"] = wallet
        return data


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['wallet_number', 'balance']
