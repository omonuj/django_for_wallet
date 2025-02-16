from django.db import router
from django.urls import path, include

urlpatterns = [
    path('register', include(router.urls)),
]