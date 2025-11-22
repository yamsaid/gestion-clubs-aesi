"""
Database initialization script
Run this after migrations to populate initial data
"""
import os
import sys
import django
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aesi_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from clubs.models import Club
from finances.models import ExpenseCategory, CashBalance

User = get_user_model()


def init_clubs():
    """Initialize clubs"""
    clubs = [
        {
            'name': "Club d'Informatique",
            'slug': 'informatique',
            'type': 'INFORMATIQUE',
            'description': 'Renforcement des compétences en informatique et nouvelles technologies',
            'email': 'informatique@aesi.bf',
        },
        {
            'name': "Club d'Anglais",
            'slug': 'anglais',
            'type': 'ANGLAIS',
            'description': 'Cadre idéal pour l\'apprentissage de l\'anglais',
            'email': 'anglais@aesi.bf',
        },
        {
            'name': "Club d'Art Oratoire",
            'slug': 'art-oratoire',
            'type': 'ART_ORATOIRE',
            'description': 'Développement des compétences de prise de parole en public',
            'email': 'art-oratoire@aesi.bf',
        },
        {
            'name': 'Club de Sport',
            'slug': 'sport',
            'type': 'SPORT',
            'description': 'Bien-être physique et mental à travers les activités sportives',
            'email': 'sport@aesi.bf',
        },
    ]
    
    for club_data in clubs:
        club, created = Club.objects.get_or_create(
            slug=club_data['slug'],
            defaults=club_data
        )
        if created:
            print(f"Created club: {club.name}")
            # Create cash balance for the club
            CashBalance.objects.create(club=club)
        else:
            print(f"Club already exists: {club.name}")


def init_expense_categories():
    """Initialize expense categories"""
    categories = [
        {'name': 'Matériel', 'color': '#3182CE', 'description': 'Achat de matériel'},
        {'name': 'Logistique', 'color': '#38A169', 'description': 'Frais logistiques'},
        {'name': 'Communication', 'color': '#805AD5', 'description': 'Communication et marketing'},
        {'name': 'Prix', 'color': '#D69E2E', 'description': 'Prix et récompenses'},
        {'name': 'Restauration', 'color': '#E53E3E', 'description': 'Restauration'},
        {'name': 'Formation', 'color': '#DD6B20', 'description': 'Formations'},
        {'name': 'Autre', 'color': '#718096', 'description': 'Autres dépenses'},
    ]
    
    for cat_data in categories:
        cat, created = ExpenseCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"Created category: {cat.name}")
        else:
            print(f"Category already exists: {cat.name}")


if __name__ == '__main__':
    print("Initializing database with default data...")
    print("-" * 50)
    
    init_clubs()
    print()
    init_expense_categories()
    
    print("-" * 50)
    print("Database initialization complete!")
