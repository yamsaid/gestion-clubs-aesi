"""
Script complet et amélioré de génération de données de test pour la plateforme AESI
Ce script crée des données réalistes et complètes pour tester TOUTES les fonctionnalités

Fonctionnalités couvertes:
- Utilisateurs (étudiants, exécutifs club, exécutifs AESI)
- Clubs et bureaux exécutifs
- Activités (planifiées, en cours, terminées, annulées)
- Participations avec OTP et feedback
- Compétitions et gagnants
- Programmes d'action et tâches
- Transactions financières et budgets
- Catégories de dépenses
- Formulaires de participation dynamiques
- Assiduité des membres exécutifs
- Photos d'activités
- Statistiques de participation

ATTENTION: Ce script est uniquement pour le développement/test!
Usage:
    python scripts/generate_test_data.py
    python scripts/generate_test_data.py --auto  # Mode automatique sans confirmation

ATTENTION: Ce script est uniquement pour le développement/test!
"""
import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta, date, time
from decimal import Decimal
import random
import string
import argparse

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aesi_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from clubs.models import (
    Club, Activity, ClubMember, ActionPlan, Task, 
    Competition, Winner, ActivityPhoto, MemberAttendance
)
from participation.models import Participation, ParticipationStats, DynamicParticipationForm
from finances.models import Transaction, CashBalance, Budget, ExpenseCategory

User = get_user_model()


# ==============================================================================
# DONNÉES DE RÉFÉRENCE
# ==============================================================================

FIRST_NAMES_M = [
    'Abdoul', 'Ibrahim', 'Moussa', 'Ousmane', 'Karim',
    'Souleymane', 'Mohamed', 'Ali', 'Boureima', 'Adama',
    'Yacouba', 'Idrissa', 'Mamadou', 'Amadou', 'Issouf',
    'Salif', 'Hamidou', 'Boubacar', 'Ismaël', 'Zakaria'
]

FIRST_NAMES_F = [
    'Fatoumata', 'Aminata', 'Mariam', 'Aissata', 'Kadiatou',
    'Hawa', 'Oumou', 'Assita', 'Salamata', 'Maimouna',
    'Zenab', 'Ramatou', 'Safiatou', 'Alimata', 'Bibata',
    'Awa', 'Fanta', 'Djénéba', 'Rokia', 'Adja'
]

LAST_NAMES = [
    'Traoré', 'Ouédraogo', 'Sawadogo', 'Kaboré', 'Compaoré',
    'Ouattara', 'Sanogo', 'Sana', 'Zongo', 'Tapsoba',
    'Ilboudo', 'Nikièma', 'Kafando', 'Coulibaly', 'Diallo',
    'Koné', 'Barro', 'Yé', 'Somé', 'Nacro', 'Zerbo',
    'Tiendrebéogo', 'Bambara', 'Kinda', 'Kinda', 'Lompo'
]

# Thèmes d'activités par club avec détails
ACTIVITY_THEMES = {
    'informatique': [
        {
            'title': 'Atelier Python pour débutants',
            'description': 'Introduction à la programmation Python avec des exercices pratiques',
            'theme': 'Programmation',
            'location': 'Salle informatique 1'
        },
        {
            'title': 'Hackathon AESI 2024',
            'description': 'Compétition de développement 24h sur le thème des solutions tech pour l\'Afrique',
            'theme': 'Innovation',
            'location': 'Amphi A'
        },
        {
            'title': 'Web Development: React & Django',
            'description': 'Développement d\'applications web modernes avec React et Django REST Framework',
            'theme': 'Développement Web',
            'location': 'Labo informatique 2'
        },
        {
            'title': 'Intelligence Artificielle et Machine Learning',
            'description': 'Introduction au ML avec scikit-learn et TensorFlow',
            'theme': 'IA & Data Science',
            'location': 'Salle ISSP'
        },
        {
            'title': 'Cybersécurité et éthique du hacking',
            'description': 'Les bases de la sécurité informatique et des bonnes pratiques',
            'theme': 'Sécurité',
            'location': 'Amphi B'
        },
        {
            'title': 'Git, GitHub et collaboration',
            'description': 'Maîtriser le versioning de code et la collaboration en équipe',
            'theme': 'Outils de développement',
            'location': 'Labo 1'
        },
        {
            'title': 'Bases de données: SQL vs NoSQL',
            'description': 'Comprendre les différences et choisir la bonne base de données',
            'theme': 'Bases de données',
            'location': 'Salle informatique 3'
        },
        {
            'title': 'Data Science avec Python',
            'description': 'Analyse de données avec pandas, numpy et matplotlib',
            'theme': 'Data Science',
            'location': 'Labo Data'
        },
        {
            'title': 'Mobile App Development',
            'description': 'Créer des applications mobiles avec Flutter',
            'theme': 'Développement Mobile',
            'location': 'Salle ISSP'
        },
        {
            'title': 'Cloud Computing et AWS',
            'description': 'Introduction au cloud computing et aux services AWS',
            'theme': 'Cloud',
            'location': 'Amphi C'
        },
    ],
    'art-oratoire': [
        {
            'title': 'Grand Concours d\'Éloquence AESI',
            'description': 'Concours annuel d\'art oratoire avec jury professionnel',
            'theme': 'Éloquence',
            'location': 'Amphi A'
        },
        {
            'title': 'Atelier de prise de parole en public',
            'description': 'Techniques pour parler avec confiance devant un public',
            'theme': 'Expression orale',
            'location': 'Salle ISSP'
        },
        {
            'title': 'Débat contradictoire: Économie numérique',
            'description': 'Débat structuré sur les enjeux de l\'économie numérique en Afrique',
            'theme': 'Débat',
            'location': 'Amphi B'
        },
        {
            'title': 'Storytelling: L\'art de raconter',
            'description': 'Techniques de narration captivante et persuasive',
            'theme': 'Narration',
            'location': 'Salle des actes'
        },
        {
            'title': 'Argumentation et rhétorique',
            'description': 'Structurer et défendre ses idées de manière convaincante',
            'theme': 'Argumentation',
            'location': 'Salle ISSP'
        },
        {
            'title': 'Expression corporelle en public',
            'description': 'Maîtriser le langage non-verbal et la gestuelle',
            'theme': 'Communication non-verbale',
            'location': 'Amphi A'
        },
        {
            'title': 'Improvisation théâtrale',
            'description': 'Développer sa spontanéité et sa créativité verbale',
            'theme': 'Improvisation',
            'location': 'Salle 12'
        },
        {
            'title': 'Slam et poésie urbaine',
            'description': 'Atelier d\'écriture et de performance de slam',
            'theme': 'Poésie',
            'location': 'Cafétéria AESI'
        },
    ],
    'anglais': [
        {
            'title': 'English Conversation Club',
            'description': 'Practice speaking English fluently in a relaxed environment',
            'theme': 'Conversation',
            'location': 'Salle ISSP'
        },
        {
            'title': 'TOEFL Preparation Workshop',
            'description': 'Intensive preparation for TOEFL exam with mock tests',
            'theme': 'Test Preparation',
            'location': 'Salle 10'
        },
        {
            'title': 'Business English for Professionals',
            'description': 'Learn professional English for the workplace',
            'theme': 'Business English',
            'location': 'Amphi B'
        },
        {
            'title': 'Movie Club: English Cinema',
            'description': 'Watch and discuss movies in English',
            'theme': 'Culture',
            'location': 'Amphi A'
        },
        {
            'title': 'Grammar Mastery Workshop',
            'description': 'Advanced English grammar concepts and exercises',
            'theme': 'Grammar',
            'location': 'Salle 8'
        },
        {
            'title': 'Pronunciation and Accent Training',
            'description': 'Improve your English pronunciation and accent',
            'theme': 'Pronunciation',
            'location': 'Labo langues'
        },
        {
            'title': 'IELTS Preparation',
            'description': 'Comprehensive IELTS exam preparation',
            'theme': 'Test Preparation',
            'location': 'Salle 15'
        },
    ],
    'sport': [
        {
            'title': 'Tournoi de Football Inter-Filières',
            'description': 'Championnat de football entre les différentes filières',
            'theme': 'Football',
            'location': 'Terrain AESI'
        },
        {
            'title': 'Basketball 3x3 Challenge',
            'description': 'Compétition de basketball 3 contre 3',
            'theme': 'Basketball',
            'location': 'Terrain basket'
        },
        {
            'title': 'Cross-country AESI 5km',
            'description': 'Course d\'endurance de 5 kilomètres',
            'theme': 'Athlétisme',
            'location': 'Piste athlétisme'
        },
        {
            'title': 'Tournoi de Volleyball Mixte',
            'description': 'Compétition de volleyball en équipes mixtes',
            'theme': 'Volleyball',
            'location': 'Terrain sport'
        },
        {
            'title': 'Football Féminin',
            'description': 'Match amical et tournoi de football féminin',
            'theme': 'Football Féminin',
            'location': 'Terrain AESI'
        },
        {
            'title': 'Fitness Challenge',
            'description': 'Défi sportif collectif et séances de remise en forme',
            'theme': 'Fitness',
            'location': 'Salle de sport'
        },
        {
            'title': 'Tennis de Table Championship',
            'description': 'Tournoi de ping-pong par équipes',
            'theme': 'Tennis de Table',
            'location': 'Salle polyvalente'
        },
        {
            'title': 'Athlétisme Multi-épreuves',
            'description': 'Compétition d\'athlétisme avec plusieurs disciplines',
            'theme': 'Athlétisme',
            'location': 'Stade municipal'
        },
        {
            'title': 'Grande Journée Sportive AESI',
            'description': 'Rassemblement sportif annuel avec diverses activités',
            'theme': 'Multi-sports',
            'location': 'Campus AESI'
        },
        {
            'title': 'Handball Tournament',
            'description': 'Tournoi de handball inter-niveaux',
            'theme': 'Handball',
            'location': 'Gymnase'
        },
    ]
}

APPRECIATION_TEXTS = [
    "Excellente activité! J'ai beaucoup appris et l'ambiance était formidable.",
    "Très instructif et bien organisé. Merci aux organisateurs!",
    "Merci pour cette opportunité d'apprentissage. Contenu de qualité.",
    "L'animateur était très compétent et pédagogue. À refaire!",
    "Activité enrichissante, j'attends la prochaine avec impatience!",
    "Bonne ambiance et contenu très intéressant. Félicitations!",
    "Je recommande vivement cette activité à tous les étudiants.",
    "Format très interactif et participatif, j'ai adoré!",
    "Activité bien menée avec une excellente organisation.",
    "Contenu de qualité avec des exemples pratiques pertinents.",
    "Super expérience! L'équipe du club a fait un travail remarquable.",
    "Très satisfait de la qualité de cette activité. Merci!",
]

SUGGESTION_TEXTS = [
    "Peut-être prévoir plus de temps pour les exercices pratiques.",
    "Ce serait bien d'avoir plus de supports visuels.",
    "Organiser ce type d'activité plus fréquemment.",
    "Inviter des professionnels externes serait un plus.",
    "Améliorer la communication avant l'événement.",
    "Prévoir des pauses entre les sessions.",
    "Diversifier les thèmes abordés.",
    "Organiser des activités similaires pour les autres niveaux.",
]

MISSION_TEMPLATES = {
    'PRESIDENT': 'Représenter le club, coordonner les activités du bureau exécutif, superviser la mise en œuvre du programme d\'action',
    'VICE_PRESIDENT': 'Assister le président dans ses fonctions, le remplacer en cas d\'absence, coordonner certains projets spécifiques',
    'SECRETARY': 'Gérer la documentation du club, rédiger les comptes-rendus, maintenir les archives',
    'TREASURER': 'Gérer les finances du club, tenir la comptabilité, préparer les rapports financiers',
    'COMMUNICATION': 'Gérer la communication interne et externe, animer les réseaux sociaux, créer les supports visuels',
    'MEMBER': 'Participer activement aux activités du club, contribuer à la réalisation des objectifs'
}


# ==============================================================================
# UTILITAIRES
# ==============================================================================

def print_header(title):
    """Afficher un en-tête formaté"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_success(message):
    """Afficher un message de succès"""
    print(f"✅ {message}")


def print_item(message):
    """Afficher un élément"""
    print(f"  ✓ {message}")


def generate_otp():
    """Générer un code OTP à 6 chiffres"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def generate_unique_link(length=10):
    """Générer un lien unique"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


# ==============================================================================
# FONCTIONS DE CRÉATION - UTILISATEURS
# ==============================================================================

def create_aesi_executives():
    """Créer des membres exécutifs AESI (administrateurs)"""
    print_header("CRÉATION DES EXÉCUTIFS AESI")
    
    executives_data = [
        {
            'first_name': 'Admin',
            'last_name': 'AESI',
            'email': 'admin@aesi.bf',
            'role': 'AESI_EXECUTIVE',
            'gender': 'M',
            'bio': 'Administrateur principal de la plateforme AESI'
        },
        {
            'first_name': 'Secrétaire',
            'last_name': 'Général',
            'email': 'secretaire@aesi.bf',
            'role': 'AESI_EXECUTIVE',
            'gender': 'F',
            'bio': 'Secrétaire général de l\'AESI'
        },
        {
            'first_name': 'Trésorier',
            'last_name': 'AESI',
            'email': 'tresorier@aesi.bf',
            'role': 'AESI_EXECUTIVE',
            'gender': 'M',
            'bio': 'Trésorier général de l\'AESI'
        }
    ]
    
    created = []
    for data in executives_data:
        user, is_created = User.objects.get_or_create(
            email=data['email'],
            defaults=data
        )
        
        if is_created:
            user.set_password('admin123')
            user.is_staff = True
            user.is_superuser = True
            user.save()
            created.append(user)
            print_item(f"{user.get_full_name()} ({user.email})")
    
    print_success(f"{len(created)} exécutifs AESI créés")
    return created


def create_students(count=60):
    """Créer des étudiants variés"""
    print_header(f"CRÉATION DE {count} ÉTUDIANTS")
    
    created = []
    existing_emails = set(User.objects.values_list('email', flat=True))
    
    attempts = 0
    max_attempts = count * 3
    
    while len(created) < count and attempts < max_attempts:
        attempts += 1
        
        gender = random.choice(['M', 'F'])
        first_name = random.choice(FIRST_NAMES_M if gender == 'M' else FIRST_NAMES_F)
        last_name = random.choice(LAST_NAMES)
        
        # Générer un email unique
        base_email = f"{first_name.lower()}.{last_name.lower()}"
        email = f"{base_email}@aesi.bf"
        counter = 1
        
        while email in existing_emails:
            email = f"{base_email}{counter}@aesi.bf"
            counter += 1
        
        user = User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            filiere=random.choice(['IDA', 'ITS', 'TSE', 'TS', 'AT']),
            niveau=random.choice(['1', '2', '3', '4']),
            role='STUDENT',
            phone=f"+226 {random.randint(60, 79)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
            bio=f"Étudiant(e) passionné(e) de {random.choice(['statistique', 'économie', 'informatique', 'mathématiques', 'analyse de données'])}."
        )
        
        user.set_password('password123')
        user.save()
        
        created.append(user)
        existing_emails.add(email)
        
        if len(created) % 10 == 0:
            print(f"  ... {len(created)} étudiants créés")
    
    print_success(f"{len(created)} étudiants créés")
    return created


# ==============================================================================
# FONCTIONS DE CRÉATION - CLUBS ET BUREAUX
# ==============================================================================

def create_club_executives():
    """Créer les bureaux exécutifs pour chaque club"""
    print_header("CRÉATION DES BUREAUX EXÉCUTIFS")
    
    clubs = Club.objects.all()
    if clubs.count() == 0:
        print("❌ ERREUR: Aucun club trouvé. Exécutez d'abord init_project.py")
        return []
    
    students = list(User.objects.filter(role='STUDENT'))
    if len(students) < 20:
        print(f"⚠️  Seulement {len(students)} étudiants disponibles")
        return []
    
    positions = ['PRESIDENT', 'VICE_PRESIDENT', 'SECRETARY', 'TREASURER', 'COMMUNICATION']
    created = []
    used_students = set()
    
    for club in clubs:
        print(f"\n📋 {club.name}:")
        
        # Sélectionner 5 étudiants différents pour le bureau
        available_students = [s for s in students if s.id not in used_students]
        if len(available_students) < 5:
            print("  ⚠️  Pas assez d'étudiants disponibles")
            continue
        
        club_students = random.sample(available_students, 5)
        
        for student, position in zip(club_students, positions):
            # Marquer comme utilisé
            used_students.add(student.id)
            
            # Promouvoir en membre exécutif de club
            student.role = 'CLUB_EXECUTIVE'
            student.save()
            
            member, is_created = ClubMember.objects.get_or_create(
                club=club,
                user=student,
                defaults={
                    'position': position,
                    'start_date': date.today() - timedelta(days=random.randint(90, 365)),
                    'is_active': True,
                    'missions': MISSION_TEMPLATES[position]
                }
            )
            
            if is_created:
                created.append(member)
                print_item(f"{student.get_full_name()} - {member.get_position_display()}")
    
    print_success(f"{len(created)} membres exécutifs créés pour {clubs.count()} clubs")
    return created


# ==============================================================================
# FONCTIONS DE CRÉATION - FINANCES
# ==============================================================================

def create_expense_categories():
    """Créer des catégories de dépenses"""
    print_header("CRÉATION DES CATÉGORIES DE DÉPENSES")
    
    categories_data = [
        {'name': 'Matériel', 'description': 'Achat de matériel et équipements', 'icon': '📦', 'color': '#3498db'},
        {'name': 'Logistique', 'description': 'Frais de logistique et organisation', 'icon': '🚚', 'color': '#2ecc71'},
        {'name': 'Communication', 'description': 'Frais de communication et marketing', 'icon': '📢', 'color': '#9b59b6'},
        {'name': 'Prix et récompenses', 'description': 'Prix pour les gagnants', 'icon': '🏆', 'color': '#f39c12'},
        {'name': 'Restauration', 'description': 'Frais de restauration', 'icon': '🍽️', 'color': '#e74c3c'},
        {'name': 'Formation', 'description': 'Frais de formation et encadrement', 'icon': '📚', 'color': '#1abc9c'},
        {'name': 'Transport', 'description': 'Frais de transport', 'icon': '🚗', 'color': '#34495e'},
        {'name': 'Impression', 'description': 'Frais d\'impression et documentation', 'icon': '🖨️', 'color': '#16a085'},
    ]
    
    created = []
    for cat_data in categories_data:
        category, is_created = ExpenseCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        
        if is_created:
            created.append(category)
            print_item(f"{cat_data['icon']} {cat_data['name']}")
    
    print_success(f"{len(created)} catégories de dépenses créées")
    return created


def create_budgets():
    """Créer des budgets pour chaque club"""
    print_header("CRÉATION DES BUDGETS")
    
    clubs = Club.objects.all()
    created = []
    
    for club in clubs:
        print(f"\n💼 {club.name}:")
        
        # Budget de l'année précédente (terminé)
        budget1, is_created1 = Budget.objects.get_or_create(
            club=club,
            title=f"Budget {date.today().year - 1}",
            defaults={
                'description': f"Budget annuel {date.today().year - 1} pour {club.name}",
                'start_date': date(date.today().year - 1, 1, 1),
                'end_date': date(date.today().year - 1, 12, 31),
                'allocated_amount': Decimal(random.randint(500000, 1000000)),
                'is_active': False
            }
        )
        
        if is_created1:
            created.append(budget1)
            print_item(f"Budget {date.today().year - 1}: {budget1.allocated_amount} FCFA")
        
        # Budget de l'année en cours
        budget2, is_created2 = Budget.objects.get_or_create(
            club=club,
            title=f"Budget {date.today().year}",
            defaults={
                'description': f"Budget annuel {date.today().year} pour {club.name}",
                'start_date': date(date.today().year, 1, 1),
                'end_date': date(date.today().year, 12, 31),
                'allocated_amount': Decimal(random.randint(600000, 1200000)),
                'is_active': True
            }
        )
        
        if is_created2:
            created.append(budget2)
            print_item(f"Budget {date.today().year}: {budget2.allocated_amount} FCFA (actif)")
    
    print_success(f"{len(created)} budgets créés")
    return created


def create_cash_balances():
    """Créer les soldes de caisse pour chaque club"""
    print_header("CRÉATION DES SOLDES DE CAISSE")
    
    clubs = Club.objects.all()
    created = []
    
    for club in clubs:
        balance, is_created = CashBalance.objects.get_or_create(
            club=club,
            defaults={
                'current_balance': Decimal('0.00')
            }
        )
        
        if is_created:
            created.append(balance)
            print_item(f"{club.name}: {balance.current_balance} FCFA")
    
    print_success(f"{len(created)} soldes de caisse créés")
    return created


# ==============================================================================
# FONCTIONS DE CRÉATION - ACTIVITÉS
# ==============================================================================

def create_activities():
    """Créer des activités variées pour tous les clubs"""
    print_header("CRÉATION DES ACTIVITÉS")
    
    clubs = Club.objects.all()
    created = []
    
    for club in clubs:
        print(f"\n📅 {club.name}:")
        
        themes = ACTIVITY_THEMES.get(club.slug, [])
        if not themes:
            print(f"  ⚠️  Pas de thèmes définis pour {club.slug}")
            continue
        
        # Créer 10-12 activités par club
        num_activities = random.randint(10, 12)
        
        for i in range(num_activities):
            # Distribution des statuts:
            # 60% terminées, 20% en cours, 15% planifiées, 5% annulées
            rand = random.random()
            if rand < 0.60:  # 60% terminées
                days_ago = random.randint(10, 200)
                activity_date = date.today() - timedelta(days=days_ago)
                status = 'COMPLETED'
            elif rand < 0.80:  # 20% en cours
                activity_date = date.today()
                status = 'ONGOING'
            elif rand < 0.95:  # 15% planifiées
                days_ahead = random.randint(5, 90)
                activity_date = date.today() + timedelta(days=days_ahead)
                status = 'PLANNED'
            else:  # 5% annulées
                days_ago = random.randint(5, 60)
                activity_date = date.today() - timedelta(days=days_ago)
                status = 'CANCELLED'
            
            theme_data = random.choice(themes)
            
            activity, is_created = Activity.objects.get_or_create(
                club=club,
                title=theme_data['title'],
                date=activity_date,
                defaults={
                    'description': theme_data['description'],
                    'theme': theme_data['theme'],
                    'time': time(hour=random.randint(14, 18), minute=random.choice([0, 30])),
                    'location': theme_data['location'],
                    'status': status,
                    'otp_enabled': True,
                    'difficulties': '' if status in ['PLANNED', 'ONGOING'] else random.choice([
                        'Aucune difficulté majeure',
                        'Quelques retards dans l\'organisation',
                        'Problème de disponibilité de la salle réglé',
                        'Budget légèrement dépassé mais activité réussie'
                    ])
                }
            )
            
            if is_created:
                created.append(activity)
                print_item(f"{activity.title} - {activity.get_status_display()} ({activity.date})")
    
    print_success(f"{len(created)} activités créées")
    return created


# ==============================================================================
# FONCTIONS DE CRÉATION - PARTICIPATIONS
# ==============================================================================

def create_participations():
    """Créer des participations pour les activités terminées"""
    print_header("CRÉATION DES PARTICIPATIONS")
    
    activities = Activity.objects.filter(status='COMPLETED')
    students = list(User.objects.filter(role='STUDENT'))
    
    if not students:
        print("❌ Aucun étudiant disponible")
        return []
    
    created = []
    
    for activity in activities:
        print(f"\n👥 {activity.title} ({activity.club.name}):")
        
        # Nombre variable de participants (25-60 par activité)
        num_participants = random.randint(25, 60)
        num_participants = min(num_participants, len(students))
        
        selected_students = random.sample(students, num_participants)
        
        for student in selected_students:
            # 90% ont vérifié leur OTP
            otp_verified = random.random() < 0.90
            
            # Parmi ceux qui ont vérifié, 85% ont soumis le feedback
            has_feedback = otp_verified and random.random() < 0.85
            
            participation, is_created = Participation.objects.get_or_create(
                activity=activity,
                user=student,
                defaults={
                    'otp_verified': otp_verified,
                    'otp_verified_at': timezone.now() - timedelta(days=(date.today() - activity.date).days) if otp_verified else None,
                    'rating': random.randint(3, 5) if has_feedback else None,
                    'appreciation': random.choice(APPRECIATION_TEXTS) if has_feedback else '',
                    'suggestion': random.choice(SUGGESTION_TEXTS) if has_feedback and random.random() < 0.6 else '',
                    'submitted_at': timezone.now() - timedelta(days=(date.today() - activity.date).days) if has_feedback else None
                }
            )
            
            if is_created:
                created.append(participation)
        
        count = len([p for p in created if p.activity == activity])
        print_item(f"{count} participants enregistrés")
    
    print_success(f"{len(created)} participations créées au total")
    return created


def create_participation_stats():
    """Créer et mettre à jour les statistiques de participation"""
    print_header("MISE À JOUR DES STATISTIQUES DE PARTICIPATION")
    
    users_with_participations = User.objects.filter(
        participations__otp_verified=True
    ).distinct()
    
    updated = []
    
    for user in users_with_participations:
        stats, created = ParticipationStats.objects.get_or_create(
            user=user
        )
        
        stats.update_stats()
        updated.append(stats)
    
    print_success(f"{len(updated)} statistiques de participation mises à jour")
    return updated


# ==============================================================================
# FONCTIONS DE CRÉATION - COMPÉTITIONS
# ==============================================================================

def create_competitions():
    """Créer des compétitions et des gagnants"""
    print_header("CRÉATION DES COMPÉTITIONS")
    
    # Activités propices aux compétitions
    competitive_keywords = ['concours', 'compétition', 'tournoi', 'hackathon', 
                           'championnat', 'match', 'challenge', 'championship']
    
    competitive_activities = Activity.objects.filter(status='COMPLETED')
    competitive_activities = [
        act for act in competitive_activities 
        if any(keyword in act.title.lower() for keyword in competitive_keywords)
    ]
    
    competitions_created = []
    winners_created = []
    
    for activity in competitive_activities:
        print(f"\n🏆 {activity.title}:")
        
        # Nombre de compétitions selon l'activité
        if 'hackathon' in activity.title.lower() or 'tournoi' in activity.title.lower():
            num_competitions = random.randint(2, 4)
        else:
            num_competitions = random.randint(1, 2)
        
        for i in range(num_competitions):
            if num_competitions > 1:
                comp_names = ['Catégorie Débutants', 'Catégorie Avancés', 'Catégorie Experts', 'Épreuve Principale']
                comp_name = comp_names[i] if i < len(comp_names) else f"Épreuve {i+1}"
            else:
                comp_name = "Compétition principale"
            
            competition, is_created = Competition.objects.get_or_create(
                activity=activity,
                name=comp_name,
                defaults={
                    'description': f"Description de la compétition: {comp_name}"
                }
            )
            
            if is_created:
                competitions_created.append(competition)
                print_item(f"{competition.name}")
                
                # Créer le podium (3 gagnants)
                participants = list(activity.participations.filter(otp_verified=True))
                
                if len(participants) >= 3:
                    winners_list = random.sample(participants, 3)
                    
                    prizes_data = [
                        ('1er Prix - Trophée + 50,000 FCFA', 1),
                        ('2ème Prix - Médaille + 30,000 FCFA', 2),
                        ('3ème Prix - Diplôme + 20,000 FCFA', 3)
                    ]
                    
                    for (prize_text, rank), winner_part in zip(prizes_data, winners_list):
                        winner, created_w = Winner.objects.get_or_create(
                            competition=competition,
                            rank=rank,
                            defaults={
                                'participant': winner_part.user,
                                'prize': prize_text
                            }
                        )
                        
                        if created_w:
                            winners_created.append(winner)
                            print(f"      🥇 Rang {rank}: {winner.participant.get_full_name()}")
    
    print_success(f"{len(competitions_created)} compétitions créées")
    print_success(f"{len(winners_created)} gagnants enregistrés")
    return competitions_created, winners_created


# ==============================================================================
# FONCTIONS DE CRÉATION - PROGRAMMES D'ACTION
# ==============================================================================

def create_action_plans():
    """Créer des programmes d'action pour chaque club"""
    print_header("CRÉATION DES PROGRAMMES D'ACTION")
    
    clubs = Club.objects.all()
    action_plans_created = []
    tasks_created = []
    
    for club in clubs:
        print(f"\n📝 {club.name}:")
        
        # 2-3 plans d'action par club
        for i in range(random.randint(2, 3)):
            if i == 0:
                # Plan de l'année dernière (terminé)
                start_date = date(date.today().year - 1, 9, 1)
                end_date = date(date.today().year, 6, 30)
                plan_title = f"Programme d'action {date.today().year - 1}/{date.today().year}"
            elif i == 1:
                # Plan en cours
                start_date = date(date.today().year, 9, 1)
                end_date = date(date.today().year + 1, 6, 30)
                plan_title = f"Programme d'action {date.today().year}/{date.today().year + 1}"
            else:
                # Plan futur
                start_date = date(date.today().year + 1, 9, 1)
                end_date = date(date.today().year + 2, 6, 30)
                plan_title = f"Programme d'action {date.today().year + 1}/{date.today().year + 2}"
            
            action_plan, is_created = ActionPlan.objects.get_or_create(
                club=club,
                title=plan_title,
                defaults={
                    'description': f"Programme d'activités et objectifs stratégiques pour {club.name}. "
                                 f"Objectifs: développer les compétences, augmenter l'engagement, "
                                 f"organiser des événements de qualité.",
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
            
            if is_created:
                action_plans_created.append(action_plan)
                print_item(f"{action_plan.title}")
                
                # Créer 8-15 tâches par plan
                club_members = list(club.members.filter(is_active=True))
                num_tasks = random.randint(8, 15)
                
                task_templates = [
                    'Organiser {count} activités de formation',
                    'Planifier et exécuter une compétition majeure',
                    'Recruter {count} nouveaux membres',
                    'Créer du contenu pour les réseaux sociaux',
                    'Établir des partenariats avec {count} organisations',
                    'Gérer le budget et les finances du club',
                    'Préparer le rapport d\'activités semestriel',
                    'Organiser une assemblée générale',
                    'Améliorer la communication interne',
                    'Développer le site web du club',
                    'Organiser un événement inter-clubs',
                    'Former les nouveaux membres du bureau',
                    'Mettre à jour la documentation du club',
                    'Organiser des sessions de feedback',
                    'Planifier le calendrier des activités'
                ]
                
                for j in range(num_tasks):
                    template = random.choice(task_templates)
                    task_title = template.format(count=random.randint(2, 5))
                    
                    # Statut de la tâche selon le plan
                    if i == 0:  # Plan passé
                        task_completed = random.random() < 0.75  # 75% complétées
                    elif i == 1:  # Plan en cours
                        task_completed = random.random() < 0.40  # 40% complétées
                    else:  # Plan futur
                        task_completed = False
                    
                    task_due_date = start_date + timedelta(days=random.randint(30, (end_date - start_date).days))
                    
                    task, created_t = Task.objects.get_or_create(
                        action_plan=action_plan,
                        title=task_title,
                        defaults={
                            'description': f"Description détaillée: {task_title}. "
                                         f"Cette tâche contribue aux objectifs stratégiques du club.",
                            'assigned_to': random.choice(club_members) if club_members else None,
                            'due_date': task_due_date,
                            'is_completed': task_completed,
                            'completed_at': timezone.now() - timedelta(days=random.randint(1, 30)) if task_completed else None
                        }
                    )
                    
                    if created_t:
                        tasks_created.append(task)
    
    print_success(f"{len(action_plans_created)} programmes d'action créés")
    print_success(f"{len(tasks_created)} tâches créées")
    return action_plans_created, tasks_created


# ==============================================================================
# FONCTIONS DE CRÉATION - TRANSACTIONS FINANCIÈRES
# ==============================================================================

def create_transactions():
    """Créer des transactions financières complètes"""
    print_header("CRÉATION DES TRANSACTIONS FINANCIÈRES")
    
    clubs = Club.objects.all()
    categories = list(ExpenseCategory.objects.all())
    
    if not categories:
        print("⚠️  Aucune catégorie de dépense, utilisation de catégories par défaut")
        categories_names = ['Matériel', 'Logistique', 'Communication', 'Prix et récompenses', 'Restauration', 'Formation']
    else:
        categories_names = [cat.name for cat in categories]
    
    income_categories = ['Subvention AESI', 'Cotisation membres', 'Partenariat', 'Don', 'Sponsoring']
    
    transactions_created = []
    
    for club in clubs:
        print(f"\n💰 {club.name}:")
        
        # Créer 4-6 revenus
        num_income = random.randint(4, 6)
        for i in range(num_income):
            transaction = Transaction.objects.create(
                club=club,
                transaction_type='INCOME',
                amount=Decimal(random.randint(150000, 600000)),
                description=f"{random.choice(income_categories)} - {date.today().year}",
                category=random.choice(income_categories),
                transaction_date=date.today() - timedelta(days=random.randint(30, 250)),
                notes=f"Reçu le {date.today()}"
            )
            transactions_created.append(transaction)
        
        # Créer des dépenses liées aux activités terminées
        completed_activities = club.activities.filter(status='COMPLETED')
        
        for activity in completed_activities:
            # 2-4 dépenses par activité
            num_expenses = random.randint(2, 4)
            
            for i in range(num_expenses):
                category = random.choice(categories_names)
                transaction = Transaction.objects.create(
                    club=club,
                    transaction_type='EXPENSE',
                    amount=Decimal(random.randint(15000, 100000)),
                    description=f"{category} pour {activity.title}",
                    category=category,
                    transaction_date=activity.date - timedelta(days=random.randint(0, 7)),
                    activity=activity,
                    notes=f"Dépense pour l'activité du {activity.date}"
                )
                transactions_created.append(transaction)
        
        # Quelques dépenses générales (non liées à des activités)
        num_general = random.randint(3, 6)
        for i in range(num_general):
            category = random.choice(categories_names)
            transaction = Transaction.objects.create(
                club=club,
                transaction_type='EXPENSE',
                amount=Decimal(random.randint(10000, 50000)),
                description=f"{category} - Frais généraux",
                category=category,
                transaction_date=date.today() - timedelta(days=random.randint(10, 200)),
                notes="Dépense générale du club"
            )
            transactions_created.append(transaction)
        
        # Mettre à jour le solde de caisse
        try:
            cash_balance = CashBalance.objects.get(club=club)
            cash_balance.update_balance()
            print_item(f"Solde final: {cash_balance.current_balance:,.0f} FCFA")
        except CashBalance.DoesNotExist:
            print_item("⚠️  Pas de CashBalance")
    
    print_success(f"{len(transactions_created)} transactions créées")
    return transactions_created


# ==============================================================================
# FONCTIONS DE CRÉATION - FORMULAIRES ET ASSIDUITÉ
# ==============================================================================

def create_dynamic_forms():
    """Créer des formulaires de participation dynamiques"""
    print_header("CRÉATION DES FORMULAIRES DE PARTICIPATION")
    
    # Activités planifiées ou en cours
    upcoming_activities = Activity.objects.filter(
        status__in=['PLANNED', 'ONGOING']
    )
    
    executives = list(User.objects.filter(role__in=['CLUB_EXECUTIVE', 'AESI_EXECUTIVE']))
    
    if not executives:
        print("⚠️  Aucun exécutif disponible")
        return []
    
    forms_created = []
    
    for activity in upcoming_activities:
        otp_code = generate_otp()
        form_link = generate_unique_link()
        
        form, is_created = DynamicParticipationForm.objects.get_or_create(
            activity=activity,
            defaults={
                'created_by': random.choice(executives),
                'otp_code': otp_code,
                'otp_expires_at': timezone.now() + timedelta(hours=random.randint(3, 24)),
                'form_link': form_link,
                'is_active': True,
                'access_count': random.randint(0, 50),
                'submission_count': random.randint(0, 30)
            }
        )
        
        if is_created:
            forms_created.append(form)
            print_item(f"{activity.title} - OTP: {otp_code} - Lien: {form_link}")
    
    print_success(f"{len(forms_created)} formulaires dynamiques créés")
    return forms_created


def create_member_attendance():
    """Créer des données d'assiduité pour les membres exécutifs"""
    print_header("CRÉATION DES DONNÉES D'ASSIDUITÉ")
    
    attendance_created = []
    
    for club in Club.objects.all():
        members = club.members.filter(is_active=True)
        completed_activities = club.activities.filter(status='COMPLETED')
        
        if not members.exists():
            continue
        
        print(f"\n📊 {club.name}:")
        
        for activity in completed_activities:
            for member in members:
                # 85% de chances de présence pour les membres exécutifs
                is_present = random.random() < 0.85
                
                attendance, is_created = MemberAttendance.objects.get_or_create(
                    member=member,
                    activity=activity,
                    defaults={
                        'is_present': is_present,
                        'notes': random.choice([
                            'Présent et actif dans l\'organisation',
                            'Présent, a contribué activement',
                            'Présent tout au long de l\'activité',
                            'Absent - Raison professionnelle',
                            'Absent excusé',
                            'Retard mais présent'
                        ]) if is_present else random.choice([
                            'Absent - Examens',
                            'Absent excusé - Raison médicale',
                            'Absent - Conflit d\'horaire'
                        ])
                    }
                )
                
                if is_created:
                    attendance_created.append(attendance)
        
        count = len([a for a in attendance_created if a.member.club == club])
        print_item(f"{count} enregistrements d'assiduité")
    
    print_success(f"{len(attendance_created)} enregistrements d'assiduité créés au total")
    return attendance_created


# ==============================================================================
# FONCTION PRINCIPALE
# ==============================================================================

def main():
    """Fonction principale d'exécution"""
    
    print("\n" + "="*70)
    print("  GÉNÉRATEUR COMPLET DE DONNÉES DE TEST - PLATEFORME AESI")
    print("="*70)
    print("\n✨ Ce script va créer des données complètes pour tester:")
    print("  • Utilisateurs (étudiants, exécutifs clubs, exécutifs AESI)")
    print("  • Bureaux exécutifs des clubs")
    print("  • Activités variées (terminées, en cours, planifiées, annulées)")
    print("  • Participations avec feedback et notes")
    print("  • Compétitions et gagnants")
    print("  • Programmes d'action et tâches")
    print("  • Catégories de dépenses")
    print("  • Budgets annuels")
    print("  • Transactions financières (revenus et dépenses)")
    print("  • Formulaires de participation dynamiques")
    print("  • Assiduité des membres exécutifs")
    print("  • Statistiques de participation")
    print("\n⚠️  ATTENTION: Script uniquement pour développement/test!")
    print("="*70)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Générer des données de test pour la plateforme AESI')
    parser.add_argument('--auto', action='store_true', help='Mode automatique sans confirmation')
    args = parser.parse_args()
    
    if not args.auto:
        try:
            response = input("\n🚀 Voulez-vous continuer? (oui/non): ")
            if response.lower() not in ['oui', 'o', 'yes', 'y']:
                print("\n❌ Opération annulée.")
                return
        except EOFError:
            print("\n⚠️  Mode interactif non disponible. Utilisez --auto pour exécuter automatiquement.")
            return
    else:
        print("\n🤖 Mode automatique activé - Génération des données en cours...")
    
    # Vérifier que les clubs existent
    if Club.objects.count() == 0:
        print("\n❌ ERREUR: Aucun club trouvé dans la base de données!")
        print("📝 Veuillez d'abord exécuter: python manage.py shell")
        print("   puis exécuter le script init_project.py ou créer les clubs manuellement")
        return
    
    print(f"\n✅ {Club.objects.count()} clubs trouvés:")
    for club in Club.objects.all():
        print(f"   • {club.name} ({club.slug})")
    
    # Créer les données dans l'ordre logique
    try:
        # 1. Utilisateurs
        aesi_execs = create_aesi_executives()
        students = create_students(60)
        
        # 2. Bureaux exécutifs
        club_executives = create_club_executives()
        
        # 3. Finances - Base
        expense_categories = create_expense_categories()
        budgets = create_budgets()
        cash_balances = create_cash_balances()
        
        # 4. Activités
        activities = create_activities()
        
        # 5. Participations
        participations = create_participations()
        participation_stats = create_participation_stats()
        
        # 6. Compétitions
        competitions, winners = create_competitions()
        
        # 7. Programmes d'action
        action_plans, tasks = create_action_plans()
        
        # 8. Transactions financières
        transactions = create_transactions()
        
        # 9. Formulaires et assiduité
        forms = create_dynamic_forms()
        attendance = create_member_attendance()
        
        # Résumé final
        print("\n" + "="*70)
        print("  📊 RÉSUMÉ DE LA CRÉATION DE DONNÉES")
        print("="*70)
        
        print("\n👥 UTILISATEURS:")
        print(f"  ✅ {len(aesi_execs)} exécutifs AESI")
        print(f"  ✅ {len(students)} étudiants")
        print(f"  ✅ {len(club_executives)} membres exécutifs de clubs")
        
        print("\n📋 CLUBS ET ACTIVITÉS:")
        print(f"  ✅ {Club.objects.count()} clubs")
        print(f"  ✅ {len(activities)} activités")
        print(f"  ✅ {len(participations)} participations")
        print(f"  ✅ {len(participation_stats)} statistiques de participation")
        
        print("\n🏆 COMPÉTITIONS:")
        print(f"  ✅ {len(competitions)} compétitions")
        print(f"  ✅ {len(winners)} gagnants")
        
        print("\n📝 PROGRAMMES D'ACTION:")
        print(f"  ✅ {len(action_plans)} programmes d'action")
        print(f"  ✅ {len(tasks)} tâches")
        
        print("\n💰 FINANCES:")
        print(f"  ✅ {len(expense_categories)} catégories de dépenses")
        print(f"  ✅ {len(budgets)} budgets")
        print(f"  ✅ {len(transactions)} transactions")
        print(f"  ✅ {len(cash_balances)} soldes de caisse")
        
        print("\n📄 FORMULAIRES ET ASSIDUITÉ:")
        print(f"  ✅ {len(forms)} formulaires de participation")
        print(f"  ✅ {len(attendance)} enregistrements d'assiduité")
        
        print("\n" + "="*70)
        print("  🎉 DONNÉES DE TEST CRÉÉES AVEC SUCCÈS!")
        print("="*70)
        
        print("\n📝 INFORMATIONS DE CONNEXION:")
        print("\n  👨‍💼 Administrateur AESI:")
        print("     Email: admin@aesi.bf")
        print("     Mot de passe: admin123")
        
        print("\n  👤 Étudiants:")
        print("     Email: [prenom].[nom]@aesi.bf (ex: abdoul.traore@aesi.bf)")
        print("     Mot de passe: password123")
        
        print("\n  📊 Membres exécutifs:")
        print("     Mêmes identifiants que ci-dessus")
        print("     (Certains étudiants ont été promus)")
        
        print("\n🚀 PROCHAINES ÉTAPES:")
        print("  1. Lancez le serveur: python manage.py runserver")
        print("  2. Accédez à l'interface: http://localhost:8000/")
        print("  3. Connectez-vous avec un des comptes ci-dessus")
        print("  4. Explorez les différentes fonctionnalités!")
        
        print("\n💡 FONCTIONNALITÉSSTESTABLES:")
        print("  • Dashboard global et par club")
        print("  • Gestion des activités")
        print("  • Participations et OTP")
        print("  • Gestion financière (transactions, budgets)")
        print("  • Programmes d'action et tâches")
        print("  • Compétitions et palmarès")
        print("  • Galerie photos")
        print("  • Statistiques et rapports")
        
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la création des données: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == '__main__':
    main()
