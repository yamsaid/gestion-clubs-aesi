"""
Forms for finances app
"""
from django import forms
from .models import Transaction, Budget
from decimal import Decimal


class IncomeForm(forms.ModelForm):
    """Form for adding income (entrée de caisse)"""
    
    class Meta:
        model = Transaction
        fields = ['amount', 'description', 'category', 'transaction_date', 'receipt', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-success focus:border-success',
                'placeholder': 'Montant en FCFA',
                'min': '0.01',
                'step': '0.01'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-success focus:border-success',
                'placeholder': 'Description de l\'entrée'
            }),
            'category': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-success focus:border-success',
                'placeholder': 'Catégorie (ex: Cotisation, Don, Subvention)'
            }),
            'transaction_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-success focus:border-success',
                'type': 'date'
            }),
            'receipt': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-success focus:border-success'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-success focus:border-success',
                'rows': 3,
                'placeholder': 'Notes additionnelles'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make receipt and notes optional
        self.fields['receipt'].required = False
        self.fields['notes'].required = False


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
