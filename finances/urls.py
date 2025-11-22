"""
URL configuration for finances app
"""
from django.urls import path
from . import views

app_name = 'finances'

urlpatterns = [
    # Transaction management
    path('club/<slug:club_slug>/', views.club_finances, name='club_finances'),
    path('club/<slug:club_slug>/add-transaction/', views.add_transaction, name='add_transaction'),
    path('transaction/<int:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transaction/<int:pk>/delete/', views.delete_transaction, name='delete_transaction'),
    
    # Budget management
    path('club/<slug:club_slug>/budgets/', views.club_budgets, name='club_budgets'),
    path('club/<slug:club_slug>/add-budget/', views.add_budget, name='add_budget'),
    path('budget/<int:pk>/', views.budget_detail, name='budget_detail'),
    
    # Reports
    path('club/<slug:club_slug>/reports/', views.financial_reports, name='financial_reports'),
]
