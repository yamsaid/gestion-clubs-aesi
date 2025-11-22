"""
API URL configuration for finances app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, BudgetViewSet, CashBalanceViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'cash-balances', CashBalanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
