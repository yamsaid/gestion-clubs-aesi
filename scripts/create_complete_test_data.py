"""
Script complet de génération de données de test pour la plateforme AESI
Ce script crée des données réalistes pour tester toutes les fonctionnalités

ATTENTION: Ce script est uniquement pour le développement/test!
"""
import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta, date, time
from decimal import Decimal
import random

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
from participation.models import Participation, DynamicParticipationForm
from finances.models import Transaction, CashBalance

User = get_user_model()


# ==============================================================================
# DONNÉES DE RÉFÉRENCE
# ==============================================================================

FIRST_NAMES_M = [
    'Abdoul', 'Ibrahim', 'Moussa', 'Ousmane', 'Karim',
    'Souleymane', 'Mohamed', 'Ali', 'Boureima', 'Adama',
    'Yacouba', 'Idrissa', 'Mamadou', 'Amadou', 'Issouf'
]

FIRST_NAMES_F = [
    'Fatoumata', 'Aminata', 'Mariam', 'Aissata', 'Kadiatou',
    'Hawa', 'Oumou', 'Assita', 'Salamata', 'Maimouna',
    'Zenab', 'Ramatou', 'Safiatou', 'Alimata', 'Bibata'
]

LAST_NAMES = [
    'Traoré', 'Ouédraogo', 'Sawadogo', 'Kaboré', 'Compaoré',
    'Ouattara', 'Sanogo', 'Sana', 'Zongo', 'Tapsoba',
    'Ilboudo', 'Nikièma', 'Kafando', 'Coulibaly', 'Diallo',
    'Koné', 'Barro', 'Yé', 'Somé', 'Nacro'
]

# Thèmes d'activités par club
ACTIVITY_THEMES = {
    'informatique': [
        ('Atelier Python', 'Programmation avancée en Python', 'Salle informatique'),
        ('Hackathon AESI', 'Compétition de développement 24h', 'Amphi A'),
        ('Web Development', 'Introduction à React et Django', 'Labo 2'),
        ('Intelligence Artificielle', 'Machine Learning avec TensorFlow', 'Salle ISSP'),
        ('Cybersécurité', 'Les bases de la sécurité informatique', 'Amphi B'),
        ('Git & GitHub', 'Collaboration et versioning de code', 'Labo 1'),
        ('Bases de données', 'SQL et NoSQL en pratique', 'Salle informatique'),
    ],
    'art-oratoire': [
        ('Concours d\'éloquence', 'Grand concours annuel d\'art oratoire', 'Amphi A'),
        ('Atelier de prise de parole', 'Techniques de communication orale', 'Salle ISSP'),
        ('Débat contradictoire', 'Débat sur l\'économie numérique', 'Amphi B'),
        ('Storytelling', 'L\'art de raconter des histoires captivantes', 'Salle des actes'),
        ('Argumentation', 'Structurer et défendre ses idées', 'Salle ISSP'),
        ('Expression corporelle', 'Le langage non-verbal en public', 'Amphi A'),
        ('Improvisation', 'Prise de parole spontanée', 'Salle 12'),
    ],
    'anglais': [
        ('English Conversation', 'Practice speaking English fluently', 'Salle ISSP'),
        ('TOEFL Preparation', 'Préparation aux tests TOEFL', 'Salle 10'),
        ('Business English', 'Anglais des affaires', 'Amphi B'),
        ('Movie Club', 'Film en anglais et discussion', 'Amphi A'),
        ('Grammar Workshop', 'Révision de la grammaire anglaise', 'Salle 8'),
        ('Pronunciation', 'Améliorer sa prononciation', 'Labo langues'),
    ],
    'sport': [
        ('Tournoi de Football', 'Championnat inter-filières de football', 'Terrain AESI'),
        ('Basketball 3x3', 'Compétition de basketball 3 contre 3', 'Terrain basket'),
        ('Cross-country', 'Course d\'endurance de 5km', 'Piste athlétisme'),
        ('Volleyball', 'Tournoi de volleyball mixte', 'Terrain sport'),
        ('Football Féminin', 'Match amical de football féminin', 'Terrain AESI'),
        ('Fitness Challenge', 'Défi sportif collectif et remise en forme', 'Salle de sport'),
        ('Tennis de Table', 'Tournoi de ping-pong', 'Salle polyvalente'),
        ('Athlétisme', 'Compétition multi-épreuves', 'Stade municipal'),
        ('Journée Sportive', 'Grand rassemblement sportif annuel', 'Campus AESI'),
    ]
}

APPRECIATION_TEXTS = [
    "Excellente activité! J'ai beaucoup appris.",
    "Très instructif et bien organisé.",
    "Merci pour cette opportunité d'apprentissage.",
    "L'animateur était très compétent.",
    "Activité enrichissante, à refaire!",
    "Bonne ambiance et contenu intéressant.",
    "Je recommande vivement cette activité.",
    "Format très intéressant, merci!",
    "Activité bien menée, félicitations!",
    "Contenu de qualité, présentation claire.",
]


# ==============================================================================
# FONCTIONS DE CRÉATION DE DONNÉES
# ==============================================================================

def create_users(count=50):
    """Créer des utilisateurs variés"""
    print(f"\n{'='*60}")
    print(f"CRÉATION DE {count} UTILISATEURS")
    print(f"{'='*60}")
    
    users_created = []
    
    for i in range(count):
        gender = random.choice(['M', 'F'])
        first_name = random.choice(FIRST_NAMES_M if gender == 'M' else FIRST_NAMES_F)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@aesi.bf"
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'gender': gender,
                'filiere': random.choice(['IDA', 'ITS', 'TSE', 'TS', 'AT']),
                'niveau': random.choice(['1', '2', '3', '4']),
                'role': 'STUDENT',
                'phone': f"+226 {random.randint(60, 79)} {random.randint(10, 99)} {random.randint(10, 99)} {random.randint(10, 99)}",
                'bio': f"Étudiant passionné en {random.choice(['statistique', 'économie', 'informatique', 'mathématiques'])}."
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            users_created.append(user)
            print(f"✓ {user.get_full_name()} ({user.email})")
    
    print(f"\n✅ {len(users_created)} utilisateurs créés")
    return users_created


def create_club_executives():
    """Créer des membres exécutifs pour chaque club"""
    print(f"\n{'='*60}")
    print("CRÉATION DES BUREAUX EXÉCUTIFS")
    print(f"{'='*60}")
    
    clubs = Club.objects.all()
    students = list(User.objects.filter(role='STUDENT')[:30])
    
    positions = ['PRESIDENT', 'VICE_PRESIDENT', 'SECRETARY', 'TREASURER', 'COMMUNICATION']
    executives_created = []
    
    for club in clubs:
        print(f"\n📋 {club.name}:")
        
        # Sélectionner 5 étudiants pour le bureau
        club_students = random.sample(students, 5)
        
        for student, position in zip(club_students, positions):
            # Promouvoir en membre exécutif de club
            student.role = 'CLUB_EXECUTIVE'
            student.save()
            
            member, created = ClubMember.objects.get_or_create(
                club=club,
                user=student,
                defaults={
                    'position': position,
                    'start_date': date.today() - timedelta(days=random.randint(90, 365)),
                    'is_active': True,
                    'missions': f"Responsable {dict(ClubMember.POSITION_CHOICES)[position]}"
                }
            )
            
            if created:
                executives_created.append(member)
                print(f"  ✓ {student.get_full_name()} - {member.get_position_display()}")
    
    print(f"\n✅ {len(executives_created)} membres exécutifs créés")
    return executives_created


def create_activities():
    """Créer des activités pour tous les clubs"""
    print(f"\n{'='*60}")
    print("CRÉATION DES ACTIVITÉS")
    print(f"{'='*60}")
    
    clubs = Club.objects.all()
    activities_created = []
    
    for club in clubs:
        print(f"\n📅 {club.name}:")
        
        themes = ACTIVITY_THEMES.get(club.slug, [
            ('Activité générale', 'Description générale', 'Salle ISSP')
        ])
        
        # Créer 7-10 activités par club
        num_activities = random.randint(7, 10)
        
        for i in range(num_activities):
            # Alterner entre activités passées et futures
            if i < 6:  # 6 activités terminées
                days_ago = random.randint(10, 180)
                activity_date = date.today() - timedelta(days=days_ago)
                status = 'COMPLETED'
            elif i < 8:  # 2 activités en cours
                activity_date = date.today()
                status = 'ONGOING'
            else:  # Activités futures
                days_ahead = random.randint(5, 60)
                activity_date = date.today() + timedelta(days=days_ahead)
                status = 'PLANNED'
            
            theme_data = random.choice(themes)
            
            activity, created = Activity.objects.get_or_create(
                club=club,
                title=f"{theme_data[0]} {i+1}",
                date=activity_date,
                defaults={
                    'description': theme_data[1],
                    'theme': theme_data[0],
                    'time': time(hour=random.randint(14, 17), minute=random.choice([0, 30])),
                    'location': theme_data[2],
                    'status': status,
                    'otp_enabled': True,
                    'difficulties': 'Aucune difficulté majeure' if status == 'COMPLETED' else ''
                }
            )
            
            if created:
                activities_created.append(activity)
                print(f"  ✓ {activity.title} - {activity.get_status_display()} ({activity.date})")
    
    print(f"\n✅ {len(activities_created)} activités créées")
    return activities_created


def create_participations():
    """Créer des participations pour les activités terminées"""
    print(f"\n{'='*60}")
    print("CRÉATION DES PARTICIPATIONS")
    print(f"{'='*60}")
    
    activities = Activity.objects.filter(status='COMPLETED')
    students = list(User.objects.filter(role='STUDENT'))
    participations_created = []
    
    for activity in activities:
        print(f"\n👥 {activity.title}:")
        
        # Nombre variable de participants (20-50)
        num_participants = random.randint(20, 50)
        selected_students = random.sample(students, min(num_participants, len(students)))
        
        for student in selected_students:
            participation, created = Participation.objects.get_or_create(
                activity=activity,
                user=student,
                defaults={
                    'otp_verified': True,
                    'otp_verified_at': timezone.now() - timedelta(days=(date.today() - activity.date).days),
                    'rating': random.randint(3, 5),
                    'appreciation': random.choice(APPRECIATION_TEXTS),
                    'submitted_at': timezone.now() - timedelta(days=(date.today() - activity.date).days)
                }
            )
            
            if created:
                participations_created.append(participation)
        
        print(f"  ✓ {len([p for p in participations_created if p.activity == activity])} participants")
    
    print(f"\n✅ {len(participations_created)} participations créées")
    return participations_created


def create_competitions():
    """Créer des compétitions et des gagnants"""
    from django.db.models import Q
    
    print(f"\n{'='*60}")
    print("CRÉATION DES COMPÉTITIONS")
    print(f"{'='*60}")
    
    # Activités propices aux compétitions
    competitive_activities = Activity.objects.filter(
        status='COMPLETED'
    ).filter(
        Q(title__icontains='concours') |
        Q(title__icontains='compétition') |
        Q(title__icontains='tournoi') |
        Q(title__icontains='hackathon') |
        Q(title__icontains='championnat') |
        Q(title__icontains='match')
    )
    
    competitions_created = []
    winners_created = []
    
    for activity in competitive_activities:
        print(f"\n🏆 {activity.title}:")
        
        # Créer 1-3 compétitions par activité
        num_competitions = random.randint(1, 3)
        
        for i in range(num_competitions):
            comp_name = f"Épreuve {i+1}" if num_competitions > 1 else "Compétition principale"
            
            competition, created = Competition.objects.get_or_create(
                activity=activity,
                name=comp_name,
                defaults={
                    'description': f"Description de la compétition {comp_name}"
                }
            )
            
            if created:
                competitions_created.append(competition)
                print(f"  ✓ {competition.name}")
                
                # Créer 3 gagnants (podium)
                participants = list(activity.participations.all()[:10])
                if len(participants) >= 3:
                    winners_list = random.sample(participants, 3)
                    
                    prizes = [
                        ('1er prix - 50,000 FCFA', '50,000 FCFA'),
                        ('2ème prix - 30,000 FCFA', '30,000 FCFA'),
                        ('3ème prix - 20,000 FCFA', '20,000 FCFA')
                    ]
                    
                    for rank, (winner_part, prize_info) in enumerate(zip(winners_list, prizes), 1):
                        winner, created_w = Winner.objects.get_or_create(
                            competition=competition,
                            rank=rank,
                            defaults={
                                'participant': winner_part.user,
                                'prize': prize_info[0]
                            }
                        )
                        
                        if created_w:
                            winners_created.append(winner)
                            print(f"    🥇 Rang {rank}: {winner.participant.get_full_name()}")
    
    print(f"\n✅ {len(competitions_created)} compétitions créées")
    print(f"✅ {len(winners_created)} gagnants enregistrés")
    return competitions_created, winners_created


def create_action_plans():
    """Créer des programmes d'action pour chaque club"""
    print(f"\n{'='*60}")
    print("CRÉATION DES PROGRAMMES D'ACTION")
    print(f"{'='*60}")
    
    clubs = Club.objects.all()
    action_plans_created = []
    tasks_created = []
    
    for club in clubs:
        print(f"\n📝 {club.name}:")
        
        # 2 plans d'action par club (un passé, un en cours)
        for i in range(2):
            if i == 0:
                start_date = date.today() - timedelta(days=180)
                end_date = date.today() - timedelta(days=30)
                plan_title = f"Programme d'action {date.today().year - 1}/{date.today().year}"
            else:
                start_date = date.today() - timedelta(days=30)
                end_date = date.today() + timedelta(days=180)
                plan_title = f"Programme d'action {date.today().year}/{date.today().year + 1}"
            
            action_plan, created = ActionPlan.objects.get_or_create(
                club=club,
                title=plan_title,
                defaults={
                    'description': f"Programme d'activités et objectifs pour {club.name}",
                    'start_date': start_date,
                    'end_date': end_date
                }
            )
            
            if created:
                action_plans_created.append(action_plan)
                print(f"  ✓ {action_plan.title}")
                
                # Créer 5-10 tâches par plan
                club_members = list(club.members.filter(is_active=True))
                num_tasks = random.randint(5, 10)
                
                for j in range(num_tasks):
                    task_completed = random.choice([True, False]) if i == 0 else random.random() < 0.3
                    
                    task, created_t = Task.objects.get_or_create(
                        action_plan=action_plan,
                        title=f"Tâche {j+1}: {random.choice(['Organiser', 'Planifier', 'Préparer', 'Coordonner'])} une activité",
                        defaults={
                            'description': f"Description détaillée de la tâche {j+1}",
                            'assigned_to': random.choice(club_members) if club_members else None,
                            'due_date': start_date + timedelta(days=random.randint(10, 150)),
                            'is_completed': task_completed,
                            'completed_at': timezone.now() if task_completed else None
                        }
                    )
                    
                    if created_t:
                        tasks_created.append(task)
    
    print(f"\n✅ {len(action_plans_created)} programmes d'action créés")
    print(f"✅ {len(tasks_created)} tâches créées")
    return action_plans_created, tasks_created


def create_transactions():
    """Créer des transactions financières pour tous les clubs"""
    print(f"\n{'='*60}")
    print("CRÉATION DES TRANSACTIONS FINANCIÈRES")
    print(f"{'='*60}")
    
    clubs = Club.objects.all()
    transactions_created = []
    
    categories_income = ['Subvention AESI', 'Cotisation membres', 'Partenariat', 'Don']
    categories_expense = ['Matériel', 'Logistique', 'Communication', 'Prix', 'Restauration', 'Formation']
    
    for club in clubs:
        print(f"\n💰 {club.name}:")
        
        # Créer 3-5 revenus
        num_income = random.randint(3, 5)
        for i in range(num_income):
            transaction = Transaction.objects.create(
                club=club,
                transaction_type='INCOME',
                amount=Decimal(random.randint(100000, 500000)),
                description=f"{random.choice(categories_income)} - Année {date.today().year}",
                category=random.choice(categories_income),
                transaction_date=date.today() - timedelta(days=random.randint(30, 180))
            )
            transactions_created.append(transaction)
        
        # Créer 10-20 dépenses liées aux activités
        completed_activities = club.activities.filter(status='COMPLETED')
        
        for activity in completed_activities:
            # 1-3 dépenses par activité
            num_expenses = random.randint(1, 3)
            
            for i in range(num_expenses):
                category = random.choice(categories_expense)
                transaction = Transaction.objects.create(
                    club=club,
                    transaction_type='EXPENSE',
                    amount=Decimal(random.randint(10000, 80000)),
                    description=f"{category} pour {activity.title}",
                    category=category,
                    transaction_date=activity.date - timedelta(days=random.randint(1, 5)),
                    activity=activity,
                    notes=f"Dépense pour l'activité du {activity.date}"
                )
                transactions_created.append(transaction)
        
        # Mettre à jour le solde
        try:
            cash_balance = CashBalance.objects.get(club=club)
            cash_balance.update_balance()
            print(f"  ✓ Solde mis à jour: {cash_balance.current_balance} FCFA")
        except CashBalance.DoesNotExist:
            print(f"  ⚠️ Pas de CashBalance pour {club.name}")
    
    print(f"\n✅ {len(transactions_created)} transactions créées")
    return transactions_created


def create_dynamic_forms():
    """Créer des formulaires de participation dynamiques"""
    print(f"\n{'='*60}")
    print("CRÉATION DES FORMULAIRES DE PARTICIPATION")
    print(f"{'='*60}")
    
    # Activités planifiées ou en cours
    upcoming_activities = Activity.objects.filter(
        status__in=['PLANNED', 'ONGOING']
    )[:10]
    
    forms_created = []
    executives = list(User.objects.filter(role__in=['CLUB_EXECUTIVE', 'AESI_EXECUTIVE']))
    
    for activity in upcoming_activities:
        # Générer un code OTP
        import uuid
        otp_code = str(random.randint(100000, 999999))
        form_link = str(uuid.uuid4())[:8]
        
        form, created = DynamicParticipationForm.objects.get_or_create(
            activity=activity,
            defaults={
                'created_by': random.choice(executives) if executives else None,
                'otp_code': otp_code,
                'otp_expires_at': timezone.now() + timedelta(hours=3),
                'form_link': form_link,
                'is_active': True
            }
        )
        
        if created:
            forms_created.append(form)
            print(f"✓ {activity.title} - OTP: {otp_code}")
    
    print(f"\n✅ {len(forms_created)} formulaires créés")
    return forms_created


def create_member_attendance():
    """Créer des données d'assiduité pour les membres exécutifs"""
    print(f"\n{'='*60}")
    print("CRÉATION DES DONNÉES D'ASSIDUITÉ")
    print(f"{'='*60}")
    
    attendance_created = []
    
    for club in Club.objects.all():
        members = club.members.filter(is_active=True)
        completed_activities = club.activities.filter(status='COMPLETED')
        
        print(f"\n📊 {club.name}:")
        
        for activity in completed_activities:
            for member in members:
                # 80% de chances de présence
                is_present = random.random() < 0.8
                
                attendance, created = MemberAttendance.objects.get_or_create(
                    member=member,
                    activity=activity,
                    defaults={
                        'is_present': is_present,
                        'notes': 'Présent et actif' if is_present else 'Absent excusé'
                    }
                )
                
                if created:
                    attendance_created.append(attendance)
        
        print(f"  ✓ {len([a for a in attendance_created if a.member.club == club])} enregistrements")
    
    print(f"\n✅ {len(attendance_created)} enregistrements d'assiduité créés")
    return attendance_created


# ==============================================================================
# FONCTION PRINCIPALE
# ==============================================================================

def main():
    """Fonction principale d'exécution"""
    from django.db.models import Q
    
    print("\n" + "="*60)
    print("  GÉNÉRATEUR DE DONNÉES DE TEST - PLATEFORME AESI")
    print("="*60)
    print("\nCe script va créer des données complètes pour tester:")
    print("  ✓ Utilisateurs et membres exécutifs")
    print("  ✓ Activités pour tous les clubs (dont Art Oratoire)")
    print("  ✓ Participations et évaluations")
    print("  ✓ Compétitions et gagnants")
    print("  ✓ Programmes d'action et tâches")
    print("  ✓ Transactions financières")
    print("  ✓ Formulaires de participation")
    print("  ✓ Assiduité des membres")
    print("\n⚠️  ATTENTION: Ceci est uniquement pour le développement!")
    print("="*60)
    
    response = input("\nVoulez-vous continuer? (oui/non): ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("\n❌ Opération annulée.")
        return
    
    # Vérifier que les clubs existent
    if Club.objects.count() == 0:
        print("\n❌ ERREUR: Aucun club trouvé!")
        print("Exécutez d'abord: python init_project.py")
        return
    
    print(f"\n✅ {Club.objects.count()} clubs trouvés")
    for club in Club.objects.all():
        print(f"   - {club.name}")
    
    # Créer les données
    try:
        users = create_users(50)
        executives = create_club_executives()
        activities = create_activities()
        participations = create_participations()
        competitions, winners = create_competitions()
        action_plans, tasks = create_action_plans()
        transactions = create_transactions()
        forms = create_dynamic_forms()
        attendance = create_member_attendance()
        
        # Résumé final
        print("\n" + "="*60)
        print("  RÉSUMÉ DE LA CRÉATION DE DONNÉES")
        print("="*60)
        print(f"\n✅ {len(users)} utilisateurs")
        print(f"✅ {len(executives)} membres exécutifs")
        print(f"✅ {len(activities)} activités")
        print(f"✅ {len(participations)} participations")
        print(f"✅ {len(competitions)} compétitions")
        print(f"✅ {len(winners)} gagnants")
        print(f"✅ {len(action_plans)} programmes d'action")
        print(f"✅ {len(tasks)} tâches")
        print(f"✅ {len(transactions)} transactions")
        print(f"✅ {len(forms)} formulaires de participation")
        print(f"✅ {len(attendance)} enregistrements d'assiduité")
        
        print("\n" + "="*60)
        print("  🎉 DONNÉES DE TEST CRÉÉES AVEC SUCCÈS!")
        print("="*60)
        print("\n📝 Informations de connexion:")
        print("   Email: admin@aesi.bf")
        print("   Mot de passe: admin123")
        print("\n   Ou tout utilisateur créé:")
        print("   Email: [prenom].[nom][n]@aesi.bf")
        print("   Mot de passe: password123")
        print("\n🚀 Lancez le serveur: python manage.py runserver")
        print("   URL: http://localhost:8000/")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de la création des données: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == '__main__':
    # Import Django Q ici pour éviter les erreurs d'import
    from django.db.models import Q
    main()
