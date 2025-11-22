"""
Serializers for finances app
"""
from rest_framework import serializers
from .models import Transaction, Budget, CashBalance, ExpenseCategory


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    club_name = serializers.CharField(source='club.name', read_only=True)
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'club', 'club_name', 'transaction_type',
            'amount', 'description', 'category', 'transaction_date',
            'activity', 'activity_title', 'receipt', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budget model"""
    club_name = serializers.CharField(source='club.name', read_only=True)
    spent_amount = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    usage_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Budget
        fields = [
            'id', 'club', 'club_name', 'title', 'description',
            'start_date', 'end_date', 'allocated_amount',
            'spent_amount', 'remaining_amount', 'usage_percentage',
            'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CashBalanceSerializer(serializers.ModelSerializer):
    """Serializer for CashBalance model"""
    club_name = serializers.CharField(source='club.name', read_only=True)
    
    class Meta:
        model = CashBalance
        fields = ['id', 'club', 'club_name', 'current_balance', 'last_updated']
        read_only_fields = ['id', 'current_balance', 'last_updated']


class ExpenseCategorySerializer(serializers.ModelSerializer):
    """Serializer for ExpenseCategory model"""
    
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'name', 'description', 'icon', 'color', 'is_active']
        read_only_fields = ['id']
