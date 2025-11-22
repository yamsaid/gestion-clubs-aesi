"""
Views for finances app
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.permissions import CanViewFinancialData
from clubs.models import Club
from .models import Transaction, Budget, CashBalance, ExpenseCategory
from .serializers import TransactionSerializer, BudgetSerializer, CashBalanceSerializer
from .forms import TransactionForm, BudgetForm


# Template views
@login_required
def club_finances(request, club_slug):
    """Club finances overview"""
    club = get_object_or_404(Club, slug=club_slug)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas accès aux données financières.")
        return redirect('clubs:club_detail', slug=club_slug)
    
    # Get or create cash balance
    cash_balance, created = CashBalance.objects.get_or_create(club=club)
    if created:
        cash_balance.update_balance()
    
    # Get recent transactions
    recent_transactions = Transaction.objects.filter(club=club)[:10]
    
    # Calculate totals
    total_income = Transaction.objects.filter(
        club=club,
        transaction_type='INCOME'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_expenses = Transaction.objects.filter(
        club=club,
        transaction_type='EXPENSE'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Get active budgets
    active_budgets = Budget.objects.filter(club=club, is_active=True)
    
    context = {
        'club': club,
        'cash_balance': cash_balance,
        'recent_transactions': recent_transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'active_budgets': active_budgets,
    }
    
    return render(request, 'finances/club_finances.html', context)


@login_required
def add_transaction(request, club_slug):
    """Add a new transaction"""
    club = get_object_or_404(Club, slug=club_slug)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission d'ajouter une transaction.")
        return redirect('clubs:club_detail', slug=club_slug)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.club = club
            transaction.created_by = request.user
            transaction.save()
            
            # Update cash balance
            cash_balance, _ = CashBalance.objects.get_or_create(club=club)
            cash_balance.update_balance()
            
            messages.success(request, "Transaction ajoutée avec succès!")
            return redirect('finances:club_finances', club_slug=club_slug)
    else:
        form = TransactionForm()
    
    context = {
        'club': club,
        'form': form,
    }
    
    return render(request, 'finances/add_transaction.html', context)


@login_required
def edit_transaction(request, pk):
    """Edit a transaction"""
    transaction = get_object_or_404(Transaction, pk=pk)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission de modifier cette transaction.")
        return redirect('finances:club_finances', club_slug=transaction.club.slug)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.updated_by = request.user
            transaction.save()
            
            # Update cash balance
            transaction.club.cash_balance.update_balance()
            
            messages.success(request, "Transaction modifiée avec succès!")
            return redirect('finances:club_finances', club_slug=transaction.club.slug)
    else:
        form = TransactionForm(instance=transaction)
    
    context = {
        'transaction': transaction,
        'form': form,
    }
    
    return render(request, 'finances/edit_transaction.html', context)


@login_required
def delete_transaction(request, pk):
    """Delete a transaction"""
    transaction = get_object_or_404(Transaction, pk=pk)
    club_slug = transaction.club.slug
    
    # Check permissions
    if not (request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Seuls les membres AESI peuvent supprimer des transactions.")
        return redirect('finances:club_finances', club_slug=club_slug)
    
    if request.method == 'POST':
        transaction.delete()
        
        # Update cash balance
        cash_balance = CashBalance.objects.get(club__slug=club_slug)
        cash_balance.update_balance()
        
        messages.success(request, "Transaction supprimée avec succès!")
        return redirect('finances:club_finances', club_slug=club_slug)
    
    return render(request, 'finances/delete_transaction.html', {'transaction': transaction})


@login_required
def club_budgets(request, club_slug):
    """Club budgets page"""
    club = get_object_or_404(Club, slug=club_slug)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas accès aux budgets.")
        return redirect('clubs:club_detail', slug=club_slug)
    
    budgets = Budget.objects.filter(club=club)
    
    context = {
        'club': club,
        'budgets': budgets,
    }
    
    return render(request, 'finances/club_budgets.html', context)


@login_required
def add_budget(request, club_slug):
    """Add a new budget"""
    club = get_object_or_404(Club, slug=club_slug)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas la permission de créer un budget.")
        return redirect('clubs:club_detail', slug=club_slug)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.club = club
            budget.created_by = request.user
            budget.save()
            
            messages.success(request, "Budget créé avec succès!")
            return redirect('finances:club_budgets', club_slug=club_slug)
    else:
        form = BudgetForm()
    
    context = {
        'club': club,
        'form': form,
    }
    
    return render(request, 'finances/add_budget.html', context)


@login_required
def budget_detail(request, pk):
    """Budget detail page"""
    budget = get_object_or_404(Budget, pk=pk)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas accès aux détails du budget.")
        return redirect('clubs:club_detail', slug=budget.club.slug)
    
    # Get related transactions
    transactions = Transaction.objects.filter(
        club=budget.club,
        transaction_date__gte=budget.start_date,
        transaction_date__lte=budget.end_date
    )
    
    context = {
        'budget': budget,
        'transactions': transactions,
    }
    
    return render(request, 'finances/budget_detail.html', context)


@login_required
def financial_reports(request, club_slug):
    """Financial reports page"""
    club = get_object_or_404(Club, slug=club_slug)
    
    # Check permissions
    if not (request.user.is_club_executive or request.user.is_aesi_executive or request.user.is_staff):
        messages.error(request, "Vous n'avez pas accès aux rapports financiers.")
        return redirect('clubs:club_detail', slug=club_slug)
    
    # Get all transactions
    transactions = Transaction.objects.filter(club=club)
    
    # Category breakdown
    category_breakdown = transactions.filter(
        transaction_type='EXPENSE'
    ).values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    context = {
        'club': club,
        'transactions': transactions,
        'category_breakdown': category_breakdown,
    }
    
    return render(request, 'finances/financial_reports.html', context)


# API ViewSets
class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for Transaction model"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, CanViewFinancialData]
    
    def get_queryset(self):
        queryset = Transaction.objects.all()
        
        # Filter by club
        club_id = self.request.query_params.get('club', None)
        if club_id:
            queryset = queryset.filter(club_id=club_id)
        
        # Filter by type
        transaction_type = self.request.query_params.get('type', None)
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        return queryset


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet for Budget model"""
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, CanViewFinancialData]
    
    def get_queryset(self):
        queryset = Budget.objects.all()
        
        # Filter by club
        club_id = self.request.query_params.get('club', None)
        if club_id:
            queryset = queryset.filter(club_id=club_id)
        
        return queryset


class CashBalanceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for CashBalance model (read-only)"""
    queryset = CashBalance.objects.all()
    serializer_class = CashBalanceSerializer
    permission_classes = [IsAuthenticated, CanViewFinancialData]
