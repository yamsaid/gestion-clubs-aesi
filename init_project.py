"""
Script d'initialisation du projet AESI Platform
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aesi_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from clubs.models import Club
from finances.models import ExpenseCategory, CashBalance

User = get_user_model()

print("=" * 60)
print("Initialisation de la plateforme AESI")
print("=" * 60)
print()

# 1. Créer le superutilisateur
print("1. Création du superutilisateur...")
if not User.objects.filter(email='admin@aesi.bf').exists():
    admin = User.objects.create_superuser(
        email='admin@aesi.bf',
        first_name='Admin',
        last_name='AESI',
        password='admin123'
    )
    print(f"✓ Superutilisateur créé: {admin.email}")
    print(f"  Email: admin@aesi.bf")
    print(f"  Mot de passe: admin123")
else:
    print("→ Superutilisateur existe déjà")
print()

# 2. Créer les 4 clubs
print("2. Création des clubs...")
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

for club_data in clubs_data:
    club, created = Club.objects.get_or_create(
        slug=club_data['slug'],
        defaults=club_data
    )
    if created:
        print(f"✓ Club créé: {club.name}")
        # Créer le solde de caisse
        CashBalance.objects.create(club=club)
    else:
        print(f"→ Club existe déjà: {club.name}")
print()

# 3. Créer les catégories de dépenses
print("3. Création des catégories de dépenses...")
categories_data = [
    {'name': 'Matériel', 'color': '#3182CE', 'description': 'Achat de matériel et équipements'},
    {'name': 'Logistique', 'color': '#38A169', 'description': 'Frais de transport, location de salles'},
    {'name': 'Communication', 'color': '#805AD5', 'description': 'Impression, affiches, communication'},
    {'name': 'Prix et Récompenses', 'color': '#D69E2E', 'description': 'Prix pour les compétitions'},
    {'name': 'Restauration', 'color': '#E53E3E', 'description': 'Repas et rafraîchissements'},
    {'name': 'Formation', 'color': '#DD6B20', 'description': 'Frais de formateurs et intervenants'},
    {'name': 'Autre', 'color': '#718096', 'description': 'Autres dépenses diverses'},
]

for cat_data in categories_data:
    cat, created = ExpenseCategory.objects.get_or_create(
        name=cat_data['name'],
        defaults=cat_data
    )
    if created:
        print(f"✓ Catégorie créée: {cat.name}")
    else:
        print(f"→ Catégorie existe déjà: {cat.name}")
print()

print("=" * 60)
print("Initialisation terminée avec succès!")
print("=" * 60)
print()
print("Informations de connexion:")
print("  URL: http://localhost:8000/")
print("  Admin: http://localhost:8000/admin/")
print("  Email: admin@aesi.bf")
print("  Mot de passe: admin123")
print()
print("Pour lancer le serveur:")
print("  python manage.py runserver")
print()
