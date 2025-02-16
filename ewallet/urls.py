from msilib.schema import ListView

from django.urls import path, include
from django.views.generic import CreateView
from rest_framework import routers

from ewallet import views
from ewallet.views import deposit_amount, withdraw_amount, view_linked_accounts, \
    receive_payment_qr_scan, get_spending_log, WalletView, UserViewSet

router = routers.DefaultRouter()
# path("user/transaction_history", get_spending_log, name='spending_logs'),
router.register('register', UserViewSet, basename='register_user')

urlpatterns = [

include(router.urls),
path("deposits", deposit_amount, name='make_payments'),
path("withdrawals", withdraw_amount, name='get_payments'),
path("balance/", WalletView.as_view(), name='get_account_balance'),
path("accounts", view_linked_accounts, name='get_linked_accounts'),
path("scan_qrcode", receive_payment_qr_scan, name='receive_qr_scan'),
path("transactions", get_spending_log, name='spending_logs'),

]