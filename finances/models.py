"""
Models for finances app
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from core.models import AuditModel


class Transaction(AuditModel):
    """Model for financial transactions"""
    
    TRANSACTION_TYPES = [
        ('INCOME', 'Entrée'),
        ('EXPENSE', 'Dépense'),
    ]
    
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name=_('club')
    )
    
    transaction_type = models.CharField(
        _('type de transaction'),
        max_length=10,
        choices=TRANSACTION_TYPES
    )
    
    amount = models.DecimalField(
        _('montant'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    description = models.CharField(_('description'), max_length=200)
    category = models.CharField(_('catégorie'), max_length=100)
    
    # Date of transaction
    transaction_date = models.DateField(_('date de transaction'))
    
    # Related activity (optional)
    activity = models.ForeignKey(
        'clubs.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name=_('activité')
    )
    
    # Supporting documents
    receipt = models.FileField(
        _('reçu'),
        upload_to='finances/receipts/',
        blank=True,
        null=True
    )
    
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')
        ordering = ['-transaction_date', '-created_at']
    
    def __str__(self):
        type_display = 'Entrée' if self.transaction_type == 'INCOME' else 'Dépense'
        return f"{self.club.name} - {type_display} - {self.amount} FCFA"


class Budget(AuditModel):
    """Model for club budgets"""
    
    club = models.ForeignKey(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name=_('club')
    )
    
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    
    # Budget period
    start_date = models.DateField(_('date de début'))
    end_date = models.DateField(_('date de fin'))
    
    # Budget amount
    allocated_amount = models.DecimalField(
        _('montant alloué'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    is_active = models.BooleanField(_('actif'), default=True)
    
    class Meta:
        verbose_name = _('budget')
        verbose_name_plural = _('budgets')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.club.name} - {self.title}"
    
    @property
    def spent_amount(self):
        """Calculate total spent amount"""
        from .models import Transaction
        total = Transaction.objects.filter(
            club=self.club,
            transaction_type='EXPENSE',
            transaction_date__gte=self.start_date,
            transaction_date__lte=self.end_date
        ).aggregate(total=models.Sum('amount'))['total']
        return total or Decimal('0.00')
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount"""
        return self.allocated_amount - self.spent_amount
    
    @property
    def usage_percentage(self):
        """Calculate budget usage percentage"""
        if self.allocated_amount == 0:
            return 0
        return round((self.spent_amount / self.allocated_amount) * 100, 2)


class CashBalance(models.Model):
    """Model for tracking club cash balance"""
    
    club = models.OneToOneField(
        'clubs.Club',
        on_delete=models.CASCADE,
        related_name='cash_balance',
        verbose_name=_('club')
    )
    
    current_balance = models.DecimalField(
        _('solde actuel'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    last_updated = models.DateTimeField(_('dernière mise à jour'), auto_now=True)
    
    class Meta:
        verbose_name = _('solde de caisse')
        verbose_name_plural = _('soldes de caisse')
    
    def __str__(self):
        return f"{self.club.name} - {self.current_balance} FCFA"
    
    def update_balance(self):
        """Recalculate balance from all transactions"""
        income = self.club.transactions.filter(
            transaction_type='INCOME'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        expenses = self.club.transactions.filter(
            transaction_type='EXPENSE'
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        self.current_balance = income - expenses
        self.save()


class ExpenseCategory(models.Model):
    """Model for expense categories"""
    
    name = models.CharField(_('nom'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icône'), max_length=50, blank=True)
    color = models.CharField(_('couleur'), max_length=7, default='#FF6B35')
    
    is_active = models.BooleanField(_('actif'), default=True)
    
    class Meta:
        verbose_name = _('catégorie de dépense')
        verbose_name_plural = _('catégories de dépenses')
        ordering = ['name']
    
    def __str__(self):
        return self.name
