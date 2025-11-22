# Plateforme de Gestion des Clubs AESI

Plateforme web pour la gestion des activités des clubs de l'Amical des Élèves Statisticiens de l'ISSP (AESI).

## Clubs Gérés
- Club d'Informatique
- Club d'Anglais
- Club d'Art Oratoire
- Club de Sport

## Fonctionnalités Principales
- Gestion des participants avec système OTP
- Suivi des activités et programmes
- Gestion des dépenses (sécurisée)
- Tableau de bord global avec statistiques
- Galerie photos des activités
- Gestion des membres exécutifs

## Stack Technique
- **Backend**: Django 4.2 LTS, Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Frontend**: Django Templates, Tailwind CSS, Alpine.js, Chart.js

## Installation

### Prérequis
- Python 3.10+
- PostgreSQL 14+
- Redis 7+

### Configuration

1. Cloner le repository
```bash
git clone <repository-url>
cd aesi_platform
```

2. Créer un environnement virtuel
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

5. Créer la base de données PostgreSQL
```bash
createdb aesi_platform_db
```

6. Appliquer les migrations
```bash
python manage.py migrate
```

7. Créer un superutilisateur
```bash
python manage.py createsuperuser
```

8. Lancer le serveur de développement
```bash
python manage.py runserver
```

9. (Optionnel) Lancer Celery pour les tâches asynchrones
```bash
celery -A aesi_platform worker -l info
```

## Structure du Projet

```
aesi_platform/
├── clubs/          # Gestion des clubs et activités
├── users/          # Authentification et profils
├── participation/  # Système de présence OTP
├── finances/       # Gestion des dépenses
├── dashboard/      # API pour tableaux de bord
├── media/          # Fichiers uploadés
└── core/           # Configuration et utilitaires
```

## Accès

- Interface admin: http://localhost:8000/admin/
- Plateforme: http://localhost:8000/

## Sécurité

- Authentification à deux facteurs pour les membres exécutifs
- Cryptage des données financières
- Système de permissions granulaires
- Audit logs complets
- Sessions sécurisées avec expiration automatique

## License

Propriétaire - AESI ISSP
