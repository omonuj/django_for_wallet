from rest_framework import serializers
from ewallet.models import Transaction, Wallet
from account.models import LinkedAccount


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    pin = serializers.CharField(write_only=True)

    def validate(self, data):
        request = self.context["request"]
        wallet = request.user.wallet
        amount = data["amount"]
        pin = data["pin"]

        linked_account = LinkedAccount.objects.filter(user=wallet.user, pin=pin).first()
        if not linked_account:
            raise serializers.ValidationError("Invalid PIN or account mismatch.")

        if wallet.balance < amount:
            raise serializers.ValidationError("Insufficient funds.")
        data["wallet"] = wallet
        return data


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['user', 'wallet_number', 'balance']
