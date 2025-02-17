from django.urls import path, include
from rest_framework import routers
from ewallet import views


urlpatterns = [
    # path("user/transaction_history", get_spending_log, name='spending_logs'),
    path("linked_accounts/", views.ViewLinkedAccounts.as_view(), name="linked_accounts"),
    path("deposit/", views.DepositView.as_view(), name='deposit'),
    path("withdraw/", views.WithdrawView.as_view(), name='withdraw'),
    path("balance/", views.BalanceView.as_view(), name='balance'),
    path("scan_qrcode/", views.receive_payment_qr_scan, name='scan_qrcode'),
    path("transactions/", views.get_spending_log, name='transactions'),
]
router = routers.DefaultRouter()