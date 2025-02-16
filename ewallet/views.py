from dbm import error
from tkinter.constants import INSERT

import segno
import requests
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from account.models import LinkedAccount
from account.serializers import UserSerializer
from ewallet.models import Wallet, Transaction, User


# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


def deposit_amount(request):
    #wallet_user = Wallet.objects.get(user=request.user)
    # if transaction_type == 'income' and amount > 0:
    #     wallet_user.balance += amount
    #     wallet_user.save()
    #
    #     transaction = Transaction()
    #     transaction.wallet = wallet_user
    #     transaction.amount = Transaction.amount
    #     transaction.transaction_type = Transaction.transaction_type
    #     transaction.save()
    # else:
    #     raise ValueError("Amount must be positive")

    wallet_user = Wallet.objects.get(user=requests)
    amount = wallet_user.deposit_amount
    wallet_number = wallet_user.wallet_number
    if wallet_number == Wallet.wallet_number and Transaction.amount > 0:
        wallet_user.balance += amount
        wallet_user.save()

    if requests.get(wallet_user):
        transaction = Transaction()
        transaction.wallet = wallet_user
        transaction.amount = Transaction.amount
        transaction.save()
        transaction.deposit(amount)
    else:
        return Response(error, status=status.HTTP_400_BAD_REQUEST)


def withdraw_amount(request, amount, balance, pin):
    wallet_user = Wallet.objects.filter(request.user)
    if amount < balance and pin == LinkedAccount.pin:
        balance = - amount
        transaction = Transaction()
        transaction.wallet = wallet_user
        transaction.amount = amount
        transaction.transaction_type = 'withdraw'
    else:
        raise ValueError("Insufficient funds")


def transfer_amount(request, sender_account, recipient_account, amount, pin):
    if sender_account.balance > 0 and pin == Wallet.wallet_pin and amount > 0:
        recipient_account.balance += amount
    else:
        raise ValueError("Insufficient funds")


class WalletView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        wallet = get_object_or_404(Wallet, user_id=request.user)
        pin = wallet
        if pin == Wallet.wallet_pin:
            return Wallet.balance
        else:
            raise ValueError("Incorrect pin, enter correct pin")


def view_linked_accounts(request):
    if request.user.is_authenticated:
        return LinkedAccount.account_number and LinkedAccount.user
    else:
        raise ValueError("User cannot be verified")


def receive_payment_qr_scan(request):
    qrcode = segno.make_qr('Call Me Teggar')
    print(qrcode.version)
    print(qrcode.data)
    qrcode.save('qrcode.png', scale=8)
    qrcode.terminal()


def send_payment_qr_scan(request):
    qrcode = segno.make_qr('')
    print(qrcode.version)
    print(qrcode.data)
    qrcode.save('qrcode.png', scale=8)
    qrcode.terminal()


def get_spending_log(request):
    wallet_user = Wallet.objects.filter(request.user)
    if request.user.is_authenticated:
        transactions = Transaction.objects.filter(wallet=wallet_user)
        return wallet_user and transactions
    else:
        raise ValueError("No transactions log available at this time")
