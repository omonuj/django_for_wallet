from django.urls import path, include
from rest_framework import routers
from ewallet.views import deposit_amount, withdraw_amount, \
    receive_payment_qr_scan, get_spending_log, WalletView, ViewLinkedAccounts


urlpatterns = [
    # path("user/transaction_history", get_spending_log, name='spending_logs'),
    path("linked_accounts/", ViewLinkedAccounts.as_view(), name="linked_accounts"),
    path("deposits/", deposit_amount, name='make_payments'),
    path("withdrawals/", withdraw_amount, name='get_payments'),
    path("balance/", WalletView.as_view(), name='get_account_balance'),
    path("scan_qrcode/", receive_payment_qr_scan, name='receive_qr_scan'),
    path("transactions/", get_spending_log, name='spending_logs'),
]