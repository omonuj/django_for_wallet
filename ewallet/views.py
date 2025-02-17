from dbm import error
from tkinter.constants import INSERT
import segno
import requests
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from account.models import LinkedAccount
from account.serializers import UserSerializer
from django.contrib.auth.models import User
from ewallet.models import Wallet, Transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ewallet.serializers import WalletSerializer, DepositSerializer, WithdrawSerializer


# Create your views here.
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DepositView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=DepositSerializer)
    def post(self, request):
        try:
            wallet = request.user.wallet
        except Wallet.DoesNotExist:
            return Response({"error": "User does not have a wallet"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DepositSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            transaction = Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type="deposit"
            )
            wallet.balance += amount
            wallet.save()
            return Response({"message": "Deposit successful", "new_balance": wallet.balance}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WithdrawView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=WithdrawSerializer)
    def post(self, request):
        serializer = WithdrawSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            wallet = serializer.validated_data["wallet"]
            amount = serializer.validated_data["amount"]
            Transaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type="withdraw"
            )
            wallet.balance -= amount
            wallet.save()
            return Response(
                {"message": "Withdrawal successful", "new_balance": wallet.balance},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BalanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ViewLinkedAccounts(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            linked_accounts = LinkedAccount.objects.filter(user=request.user)
            return Response({"linked_accounts": list(linked_accounts.values())}, status=200)
        else:
            raise ValueError("User cannot be verified")


def transfer_amount(request, sender_account, recipient_account, amount, pin):
    if sender_account.wallet_pin != pin:
        raise ValueError("Incorrect PIN")
    if sender_account.balance >= amount:
        sender_account.balance -= amount
        recipient_account.balance += amount
        sender_account.save()
        recipient_account.save()
    else:
        raise ValueError("Insufficient funds")


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
