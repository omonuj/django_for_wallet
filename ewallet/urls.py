from django.urls import path, include
from rest_framework import routers
from ewallet import views


urlpatterns = [
    # path("user/transaction_history", get_spending_log, name='spending_logs'),
    path("linked_accounts/", views.ViewLinkedAccounts.as_view(), name="linked_accounts"),
    path("deposit/", views.DepositView.as_view(), name='deposit'),
    path("withdraw/", views.WithdrawView.as_view(), name='withdraw'),
    path("balance/", views.BalanceView.as_view(), name='balance'),
    path("transfer_money/", views.TransferAmountView.as_view(), name='transfer_money'),
    path("receive_payment_qr_scan/", views.ReceivePaymentQRScan.as_view(), name='receive_payment_qr_scan'),
    path("send_payment_qr_scan/", views.SendPaymentQRScan.as_view(), name='send_payment_qr_scan'),
    path("transactions/", views.get_spending_log, name='transactions'),
]
router = routers.DefaultRouter()