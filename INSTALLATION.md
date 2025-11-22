# Guide d'Installation - AESI Platform

## Prérequis

- Python 3.10 ou supérieur
- PostgreSQL 14 ou supérieur
- Redis 7 ou supérieur
- Git

## Installation Locale

### 1. Cloner le projet

```bash
git clone <repository-url>
cd aesi_platform
```

### 2. Créer un environnement virtuel

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Copier le fichier `.env.example` vers `.env`:

```bash
cp .env.example .env
```

Modifier le fichier `.env` avec vos configurations:

```env
# Django Settings
SECRET_KEY=votre-clé-secrète-unique
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=aesi_platform_db
DB_USER=postgres
DB_PASSWORD=votre-mot-de-passe
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (optionnel pour le développement)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### 5. Créer la base de données PostgreSQL

**Windows (PowerShell):**
```powershell
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE aesi_platform_db;
\q
```

**Linux/Mac:**
```bash
# Créer la base de données
createdb aesi_platform_db
```

### 6. Appliquer les migrations

```bash
python manage.py migrate
```

### 7. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer votre compte administrateur.

### 8. Charger les données initiales (optionnel)

```bash
python manage.py loaddata initial_data.json
```

### 9. Collecter les fichiers statiques

```bash
python manage.py collectstatic --noinput
```

### 10. Lancer le serveur de développement

**Terminal 1 - Serveur Django:**
```bash
python manage.py runserver
```

**Terminal 2 - Redis (si pas déjà lancé):**
```bash
redis-server
```

**Terminal 3 - Celery Worker (optionnel):**
```bash
celery -A aesi_platform worker -l info
```

### 11. Accéder à l'application

- **Application:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/

## Installation avec Docker

### 1. Prérequis

- Docker Desktop
- Docker Compose

### 2. Lancer avec Docker Compose

```bash
# Construire et lancer les conteneurs
docker-compose up --build

# En mode détaché
docker-compose up -d
```

### 3. Appliquer les migrations

```bash
docker-compose exec web python manage.py migrate
```

### 4. Créer un superutilisateur

```bash
docker-compose exec web python manage.py createsuperuser
```

### 5. Accéder à l'application

- **Application:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/

## Configuration des Clubs

### 1. Créer les clubs dans l'admin

1. Connectez-vous à l'admin: http://localhost:8000/admin/
2. Allez dans **Clubs** > **Clubs**
3. Créez les 4 clubs:
   - Club d'Informatique (slug: `informatique`, type: `INFORMATIQUE`)
   - Club d'Anglais (slug: `anglais`, type: `ANGLAIS`)
   - Club d'Art Oratoire (slug: `art-oratoire`, type: `ART_ORATOIRE`)
   - Club de Sport (slug: `sport`, type: `SPORT`)

### 2. Créer des membres exécutifs

1. Créez d'abord des utilisateurs avec le rôle "Membre exécutif de club"
2. Allez dans **Clubs** > **Membres exécutifs**
3. Assignez les utilisateurs aux clubs avec leurs postes respectifs

### 3. Créer des catégories de dépenses

1. Allez dans **Finances** > **Catégories de dépenses**
2. Créez des catégories comme:
   - Matériel
   - Logistique
   - Communication
   - Prix/Récompenses
   - Autre

## Tests

### Lancer les tests

```bash
python manage.py test
```

### Lancer les tests avec couverture

```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Déploiement

### Prérequis pour la production

1. Configurer les variables d'environnement:
   ```env
   DEBUG=False
   SECRET_KEY=une-clé-très-sécurisée-et-unique
   ALLOWED_HOSTS=votre-domaine.com
   ```

2. Utiliser une base de données PostgreSQL hébergée

3. Configurer un service de stockage de fichiers (AWS S3, etc.)

4. Configurer le serveur SMTP pour les emails

### Déploiement sur Heroku

```bash
# Installer Heroku CLI
heroku login

# Créer une application
heroku create aesi-platform

# Ajouter PostgreSQL
heroku addons:create heroku-postgresql:mini

# Ajouter Redis
heroku addons:create heroku-redis:mini

# Configurer les variables d'environnement
heroku config:set SECRET_KEY=votre-clé-secrète
heroku config:set DEBUG=False

# Déployer
git push heroku main

# Appliquer les migrations
heroku run python manage.py migrate

# Créer un superutilisateur
heroku run python manage.py createsuperuser
```

## Dépannage

### Erreur de connexion à la base de données

- Vérifiez que PostgreSQL est bien lancé
- Vérifiez les credentials dans le fichier `.env`
- Vérifiez que la base de données existe

### Erreur de connexion à Redis

- Vérifiez que Redis est bien lancé
- Vérifiez l'URL Redis dans le fichier `.env`

### Erreur lors des migrations

```bash
# Réinitialiser les migrations (ATTENTION: supprime les données)
python manage.py migrate --fake-initial
```

### Problèmes de permissions

- Vérifiez que l'utilisateur a les bonnes permissions dans la base de données
- Vérifiez les permissions des fichiers et dossiers

## Support

Pour toute question ou problème:
- Consultez la documentation: [lien vers la doc]
- Ouvrez une issue sur GitHub
- Contactez l'équipe AESI

## License

Propriétaire - AESI ISSP © 2024
