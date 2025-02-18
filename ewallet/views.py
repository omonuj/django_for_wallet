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
from django.contrib.auth.hashers import check_password
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


class TransferAmountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender = request.user.wallet.wallet_number
        recipient = request.data.get("recipient_wallet")
        amount = request.data.get("amount")
        pin = request.data.get("pin")

        if not recipient or not amount or not pin:
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
        if sender == recipient:
            return Response({"error": "You cant send money to your self"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            sender_wallet = get_object_or_404(Wallet, wallet_number=sender)
            recipient_wallet = get_object_or_404(Wallet, wallet_number=recipient)

            print("------------Sender--------------")
            print(sender_wallet)
            print("------------Recipient--------------")
            print(recipient_wallet)

            if sender_wallet.check_pin(pin):
                return Response({"error": "Incorrect PIN"}, status=status.HTTP_403_FORBIDDEN)

            # amount = float(amount)
            if sender_wallet.balance < amount:
                return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)

            sender_wallet.balance -= amount
            recipient_wallet.balance += amount
            sender_wallet.save()
            recipient_wallet.save()

            Transaction.objects.create(
                wallet=sender_wallet,
                amount=amount,
                transaction_type='expense'
            )

            Transaction.objects.create(
                wallet=recipient_wallet,
                amount=amount,
                transaction_type='income'
            )
            return Response({"message": "Transfer successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
