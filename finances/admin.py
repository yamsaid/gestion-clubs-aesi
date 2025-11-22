"""
Admin configuration for finances app
"""
from django.contrib import admin
from .models import Transaction, Budget, CashBalance, ExpenseCategory


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'club', 'transaction_type', 'amount', 'description',
        'category', 'transaction_date', 'activity'
    ]
    list_filter = [
        'transaction_type', 'club', 'category', 'transaction_date'
    ]
    search_fields = ['description', 'notes', 'club__name']
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('club', 'transaction_type', 'amount', 'transaction_date')
        }),
        ('Détails', {
            'fields': ('description', 'category', 'activity', 'notes')
        }),
        ('Documents', {
            'fields': ('receipt',)
        }),
        ('Audit', {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'club', 'allocated_amount', 'spent_amount',
        'remaining_amount', 'usage_percentage', 'start_date',
        'end_date', 'is_active'
    ]
    list_filter = ['club', 'is_active', 'start_date']
    search_fields = ['title', 'description', 'club__name']
    date_hierarchy = 'start_date'
    
    readonly_fields = [
        'spent_amount', 'remaining_amount', 'usage_percentage',
        'created_by', 'updated_by', 'created_at', 'updated_at'
    ]


@admin.register(CashBalance)
class CashBalanceAdmin(admin.ModelAdmin):
    list_display = ['club', 'current_balance', 'last_updated']
    list_filter = ['club']
    search_fields = ['club__name']
    readonly_fields = ['last_updated']
    
    actions = ['update_balances']
    
    def update_balances(self, request, queryset):
        """Action to update balances"""
        count = 0
        for balance in queryset:
            balance.update_balance()
            count += 1
        self.message_user(
            request,
            f'{count} soldes mis à jour avec succès.'
        )
    update_balances.short_description = "Mettre à jour les soldes"


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
