"""
Setup script for AESI Platform
This script helps initialize the project with basic data
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aesi_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from clubs.models import Club
from finances.models import ExpenseCategory

User = get_user_model()


def create_clubs():
    """Create the 4 main clubs"""
    clubs_data = [
        {
            'name': "Club d'Informatique",
            'slug': 'informatique',
            'type': 'INFORMATIQUE',
            'description': "Le Club d'Informatique de l'AESI vise à renforcer les compétences des étudiants en informatique et nouvelles technologies. Nous organisons des ateliers, des formations et des compétitions pour développer l'expertise technique de nos membres.",
            'email': 'informatique@aesi.bf',
        },
        {
            'name': "Club d'Anglais",
            'slug': 'anglais',
            'type': 'ANGLAIS',
            'description': "Le Club d'Anglais offre un cadre idéal pour l'apprentissage et la pratique de l'anglais. À travers des sessions de conversation, des débats et des activités ludiques, nous aidons les étudiants à améliorer leur maîtrise de la langue anglaise.",
            'email': 'anglais@aesi.bf',
        },
        {
            'name': "Club d'Art Oratoire",
            'slug': 'art-oratoire',
            'type': 'ART_ORATOIRE',
            'description': "Le Club d'Art Oratoire développe les compétences de prise de parole en public. Nous organisons des sessions de formation, des concours d'éloquence et des débats pour aider nos membres à devenir des orateurs confiants et persuasifs.",
            'email': 'art-oratoire@aesi.bf',
        },
        {
            'name': 'Club de Sport',
            'slug': 'sport',
            'type': 'SPORT',
            'description': "Le Club de Sport promeut le bien-être physique et mental à travers diverses activités sportives. Football, basketball, athlétisme... nous organisons des compétitions et des séances d'entraînement régulières pour maintenir nos membres en forme.",
            'email': 'sport@aesi.bf',
        },
    ]
    
    print("Création des clubs...")
    for club_data in clubs_data:
        club, created = Club.objects.get_or_create(
            slug=club_data['slug'],
            defaults=club_data
        )
        if created:
            print(f"✓ Club créé: {club.name}")
        else:
            print(f"→ Club existe déjà: {club.name}")
    
    print(f"\nTotal: {Club.objects.count()} clubs dans la base de données\n")


def create_expense_categories():
    """Create expense categories"""
    categories_data = [
        {
            'name': 'Matériel',
            'description': 'Achat de matériel et équipements',
            'color': '#3182CE',
            'icon': '📦',
        },
        {
            'name': 'Logistique',
            'description': 'Frais de transport, location de salles, etc.',
            'color': '#38A169',
            'icon': '🚚',
        },
        {
            'name': 'Communication',
            'description': 'Impression, affiches, communication digitale',
            'color': '#805AD5',
            'icon': '📢',
        },
        {
            'name': 'Prix et Récompenses',
            'description': 'Prix pour les compétitions et gagnants',
            'color': '#D69E2E',
            'icon': '🏆',
        },
        {
            'name': 'Restauration',
            'description': 'Repas et rafraîchissements',
            'color': '#E53E3E',
            'icon': '🍽️',
        },
        {
            'name': 'Formation',
            'description': 'Frais de formateurs et intervenants',
            'color': '#DD6B20',
            'icon': '👨‍🏫',
        },
        {
            'name': 'Autre',
            'description': 'Autres dépenses diverses',
            'color': '#718096',
            'icon': '📝',
        },
    ]
    
    print("Création des catégories de dépenses...")
    for category_data in categories_data:
        category, created = ExpenseCategory.objects.get_or_create(
            name=category_data['name'],
            defaults=category_data
        )
        if created:
            print(f"✓ Catégorie créée: {category.name}")
        else:
            print(f"→ Catégorie existe déjà: {category.name}")
    
    print(f"\nTotal: {ExpenseCategory.objects.count()} catégories dans la base de données\n")


def create_superuser():
    """Create a superuser if none exists"""
    if User.objects.filter(is_superuser=True).exists():
        print("Un superutilisateur existe déjà.\n")
        return
    
    print("Création d'un superutilisateur...")
    print("Veuillez entrer les informations suivantes:\n")
    
    email = input("Email: ")
    first_name = input("Prénom: ")
    last_name = input("Nom: ")
    password = input("Mot de passe: ")
    
    user = User.objects.create_superuser(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password
    )
    
    print(f"\n✓ Superutilisateur créé: {user.email}\n")


def main():
    """Main setup function"""
    print("=" * 60)
    print("Configuration initiale de la plateforme AESI")
    print("=" * 60)
    print()
    
    # Create clubs
    create_clubs()
    
    # Create expense categories
    create_expense_categories()
    
    # Create superuser
    create_superuser_choice = input("Voulez-vous créer un superutilisateur? (o/n): ")
    if create_superuser_choice.lower() == 'o':
        create_superuser()
    
    print("=" * 60)
    print("Configuration terminée avec succès!")
    print("=" * 60)
    print()
    print("Prochaines étapes:")
    print("1. Lancez le serveur: python manage.py runserver")
    print("2. Accédez à l'admin: http://localhost:8000/admin/")
    print("3. Créez des membres exécutifs pour chaque club")
    print("4. Commencez à ajouter des activités!")
    print()


if __name__ == '__main__':
    main()
