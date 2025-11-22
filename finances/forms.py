"""
Forms for finances app
"""
from django import forms
from .models import Transaction, Budget


class TransactionForm(forms.ModelForm):
    """Form for Transaction model"""
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_type', 'amount', 'description',
            'category', 'transaction_date', 'activity',
            'receipt', 'notes'
        ]
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class BudgetForm(forms.ModelForm):
    """Form for Budget model"""
    
    class Meta:
        model = Budget
        fields = [
            'title', 'description', 'start_date',
            'end_date', 'allocated_amount', 'is_active'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
