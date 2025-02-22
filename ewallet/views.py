import os
import uuid
import segno
import requests
import base64
from io import BytesIO
from dbm import error
from tkinter.constants import INSERT
from cryptography.fernet import Fernet
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.conf import settings
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
from ewallet.models import Wallet, Transaction, TransactionQRScan
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ewallet.serializers import WalletSerializer, DepositSerializer, WithdrawSerializer
from PIL import Image, ImageDraw, ImageFont
from decimal import Decimal


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


class ReceivePaymentQRScan(APIView):

    def post(self, request):
        user_wallet = get_object_or_404(Wallet, user=request.user)
        amount = request.data.get("amount")

        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        recipient_account_number = user_wallet.wallet_number
        qr_data = f"{recipient_account_number}|{amount}"

        # Encrypt QR data
        cipher = Fernet(settings.QR_ENCRYPTION_KEY.encode())
        encrypted_qr_data = cipher.encrypt(qr_data.encode()).decode()

        # Generate QR with encrypted data
        qr = segno.make_qr(encrypted_qr_data)
        buffer = BytesIO()
        qr.save(buffer, kind='png', scale=8)
        buffer.seek(0)

        # Convert QR code to PIL Image
        qr_img = Image.open(buffer)

        # Load logo (Ensure logo exists in media directory)
        logo_path = os.path.join(settings.BASE_DIR, "media", "img", "genas_logo.jpg")
        if os.path.exists(logo_path):
            logo = Image.open(logo_path).convert("RGBA")

            # Resize logo
            logo_size = qr_img.size[0] // 5  # 20% of QR code size
            logo = logo.resize((logo_size, logo_size))

            # Paste logo in the center of QR code
            qr_center = ((qr_img.size[0] - logo_size) // 2, (qr_img.size[1] - logo_size) // 2)
            qr_img.paste(logo, qr_center, mask=logo)

        # Add text (Optional: "Genas Wallet")
        # draw = ImageDraw.Draw(qr_img)
        # font_path = os.path.join(settings.BASE_DIR, "static", "arial.ttf")  # Use a font file
        # if os.path.exists(font_path):
        #     font = ImageFont.truetype(font_path, 20)
        #     text = "Genas Wallet"
        #     text_size = draw.textsize(text, font=font)
        #     text_position = ((qr_img.size[0] - text_size[0]) // 2, qr_img.size[1] - 30)
        #     draw.text(text_position, text, font=font, fill="black")

        # Save QR code with customizations
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        # Create Transaction
        transaction = TransactionQRScan.objects.create(
            wallet=user_wallet,
            amount=amount,
            recipient_account_number=recipient_account_number
        )

        # Save the QR code image
        qr_filename = f"{uuid.uuid4().hex}.png"
        transaction.qr_code.save(qr_filename, ContentFile(qr_buffer.read()), save=True)

        return Response({
            "message": "QR Code generated successfully",
            "qr_code_url": transaction.qr_code.url,
        }, status=status.HTTP_201_CREATED)


class SendPaymentQRScan(APIView):
    def post(self, request):
        qr_data = request.data.get("qr_data")
        if not qr_data:
            return Response({"error": "QR data is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cipher = Fernet(settings.QR_ENCRYPTION_KEY.encode())
            decrypted_qr_data = cipher.decrypt(qr_data.encode()).decode()
            recipient_account_number, amount = decrypted_qr_data.split("|")
            print(f"""
                account_number: {recipient_account_number}
                amount: {amount}
            """)
            amount = Decimal(amount)
            sender_wallet = get_object_or_404(Wallet, user=request.user)
            recipient_wallet = get_object_or_404(Wallet, wallet_number=recipient_account_number)
            if sender_wallet.balance < amount:
                return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
            sender_wallet.balance -= amount
            recipient_wallet.balance += amount
            sender_wallet.save()
            recipient_wallet.save()
            return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def get_spending_log(request):
    wallet_user = Wallet.objects.filter(request.user)
    if request.user.is_authenticated:
        transactions = Transaction.objects.filter(wallet=wallet_user)
        return wallet_user and transactions
    else:
        raise ValueError("No transactions log available at this time")
