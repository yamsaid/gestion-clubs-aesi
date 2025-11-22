"""
Create sample data for testing
WARNING: This is for development only!
"""
import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aesi_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from clubs.models import Club, Activity, ClubMember
from participation.models import Participation
from finances.models import Transaction

User = get_user_model()


def create_sample_users(count=20):
    """Create sample users"""
    print(f"Creating {count} sample users...")
    
    filieres = ['IDA', 'ITS', 'TSE', 'TS', 'AT']
    niveaux = ['1', '2', '3', '4']
    
    users = []
    for i in range(count):
        email = f"user{i+1}@aesi.bf"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': f'Prénom{i+1}',
                'last_name': f'Nom{i+1}',
                'filiere': random.choice(filieres),
                'niveau': random.choice(niveaux),
                'role': 'STUDENT',
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            users.append(user)
            print(f"Created user: {user.email}")
    
    return users


def create_sample_activities():
    """Create sample activities for each club"""
    print("Creating sample activities...")
    
    clubs = Club.objects.all()
    
    for club in clubs:
        for i in range(5):
            date = datetime.now().date() - timedelta(days=random.randint(1, 90))
            
            activity, created = Activity.objects.get_or_create(
                club=club,
                title=f"Activité {i+1} - {club.name}",
                defaults={
                    'description': f"Description de l'activité {i+1}",
                    'theme': f"Thème {i+1}",
                    'date': date,
                    'location': 'Salle ISSP',
                    'status': 'COMPLETED' if i < 3 else 'PLANNED',
                }
            )
            
            if created:
                print(f"Created activity: {activity.title}")


def create_sample_participations():
    """Create sample participations"""
    print("Creating sample participations...")
    
    users = User.objects.filter(role='STUDENT')
    activities = Activity.objects.filter(status='COMPLETED')
    
    for activity in activities:
        # Random number of participants per activity
        num_participants = random.randint(5, 15)
        selected_users = random.sample(list(users), min(num_participants, len(users)))
        
        for user in selected_users:
            participation, created = Participation.objects.get_or_create(
                activity=activity,
                user=user,
                defaults={
                    'otp_verified': True,
                    'otp_verified_at': datetime.now(),
                    'rating': random.randint(3, 5),
                    'appreciation': 'Très bonne activité!',
                    'submitted_at': datetime.now(),
                }
            )
            
            if created:
                print(f"Created participation: {user.email} -> {activity.title}")


def create_sample_transactions():
    """Create sample transactions"""
    print("Creating sample transactions...")
    
    clubs = Club.objects.all()
    categories = ['Matériel', 'Logistique', 'Communication', 'Prix', 'Restauration']
    
    for club in clubs:
        # Create some income
        for i in range(2):
            Transaction.objects.create(
                club=club,
                transaction_type='INCOME',
                amount=Decimal(random.randint(50000, 200000)),
                description=f'Subvention {i+1}',
                category='Subvention',
                transaction_date=datetime.now().date() - timedelta(days=random.randint(1, 60))
            )
        
        # Create some expenses
        for i in range(5):
            Transaction.objects.create(
                club=club,
                transaction_type='EXPENSE',
                amount=Decimal(random.randint(5000, 50000)),
                description=f'Dépense {i+1}',
                category=random.choice(categories),
                transaction_date=datetime.now().date() - timedelta(days=random.randint(1, 60))
            )
        
        # Update cash balance
        club.cash_balance.update_balance()
        print(f"Created transactions for: {club.name}")


if __name__ == '__main__':
    print("=" * 60)
    print("Creating sample data for AESI Platform")
    print("WARNING: This is for development/testing only!")
    print("=" * 60)
    print()
    
    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        sys.exit(0)
    
    create_sample_users(20)
    print()
    create_sample_activities()
    print()
    create_sample_participations()
    print()
    create_sample_transactions()
    
    print()
    print("=" * 60)
    print("Sample data creation complete!")
    print("=" * 60)
