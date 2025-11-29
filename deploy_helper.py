#!/usr/bin/env python
"""
Script d'aide au déploiement sur PythonAnywhere
Usage: python deploy_helper.py [commande]
"""

import os
import sys
import subprocess
from pathlib import Path


class DeployHelper:
    """Assistant de déploiement pour PythonAnywhere"""
    
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'reset': '\033[0m'
        }
    
    def print_color(self, text, color='reset'):
        """Affiche du texte en couleur"""
        print(f"{self.colors.get(color, '')}{text}{self.colors['reset']}")
    
    def print_header(self, text):
        """Affiche un header"""
        self.print_color("\n" + "=" * 70, 'blue')
        self.print_color(f"  {text}", 'blue')
        self.print_color("=" * 70, 'blue')
    
    def print_success(self, text):
        """Affiche un message de succès"""
        self.print_color(f"✅ {text}", 'green')
    
    def print_error(self, text):
        """Affiche un message d'erreur"""
        self.print_color(f"❌ {text}", 'red')
    
    def print_warning(self, text):
        """Affiche un avertissement"""
        self.print_color(f"⚠️  {text}", 'yellow')
    
    def print_info(self, text):
        """Affiche une info"""
        print(f"ℹ️  {text}")
    
    def run_command(self, command, description=""):
        """Exécute une commande shell"""
        if description:
            self.print_info(description)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def check_requirements(self):
        """Vérifie que les prérequis sont installés"""
        self.print_header("Vérification des Prérequis")
        
        requirements = {
            'Python': 'python --version',
            'Git': 'git --version',
            'Django': 'python -c "import django; print(django.get_version())"'
        }
        
        all_ok = True
        for name, command in requirements.items():
            success, output = self.run_command(command)
            if success:
                self.print_success(f"{name}: {output.strip()}")
            else:
                self.print_error(f"{name}: Non trouvé")
                all_ok = False
        
        return all_ok
    
    def generate_secret_key(self):
        """Génère une SECRET_KEY Django"""
        self.print_header("Génération de SECRET_KEY")
        
        command = 'python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'
        success, secret_key = self.run_command(command)
        
        if success:
            self.print_success("SECRET_KEY générée:")
            print(f"\n{secret_key.strip()}\n")
            self.print_warning("⚠️  Copiez cette clé dans votre fichier .env!")
            return secret_key.strip()
        else:
            self.print_error("Erreur lors de la génération de la clé")
            return None
    
    def create_requirements_pa(self):
        """Crée requirements_pythonanywhere.txt"""
        self.print_header("Création de requirements_pythonanywhere.txt")
        
        packages = [
            "Django==4.2.7",
            "djangorestframework==3.14.0",
            "django-filter==23.3",
            "mysqlclient==2.2.0",
            "django-allauth==0.57.0",
            "PyJWT==2.8.0",
            "djangorestframework-simplejwt==5.3.0",
            "Pillow==10.1.0",
            "argon2-cffi==23.1.0",
            "django-cors-headers==4.3.0",
            "python-decouple==3.8",
            "whitenoise==6.6.0",
            "django-crispy-forms==2.1",
            "crispy-tailwind==0.5.0",
            "plotly==5.18.0",
            "kaleido==0.2.1",
        ]
        
        filepath = self.base_dir / "requirements_pythonanywhere.txt"
        
        try:
            with open(filepath, 'w') as f:
                f.write("# Requirements optimisés pour PythonAnywhere\n")
                f.write("# Généré automatiquement\n\n")
                for package in packages:
                    f.write(f"{package}\n")
            
            self.print_success(f"Fichier créé: {filepath}")
            self.print_info("Packages inclus:")
            for package in packages:
                print(f"  - {package}")
            return True
        except Exception as e:
            self.print_error(f"Erreur: {e}")
            return False
    
    def create_env_template(self):
        """Crée un template .env.pythonanywhere"""
        self.print_header("Création du Template .env")
        
        username = input("Entrez votre username PythonAnywhere: ").strip()
        
        if not username:
            self.print_error("Username requis!")
            return False
        
        secret_key = self.generate_secret_key()
        
        env_template = f"""# Configuration pour PythonAnywhere
# Généré automatiquement

# Django Settings
SECRET_KEY={secret_key}
DEBUG=False
ALLOWED_HOSTS={username}.pythonanywhere.com

# Database MySQL
DB_NAME={username}$aesi_db
DB_USER={username}
DB_PASSWORD=VOTRE_MOT_DE_PASSE_MYSQL_ICI
DB_HOST={username}.mysql.pythonanywhere-services.com
DB_PORT=3306

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Security
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# OTP Settings
OTP_VALIDITY_MINUTES=180

# Paths (automatiques)
MEDIA_ROOT=/home/{username}/aesi-platform/media/
STATIC_ROOT=/home/{username}/aesi-platform/staticfiles/
"""
        
        filepath = self.base_dir / ".env.pythonanywhere"
        
        try:
            with open(filepath, 'w') as f:
                f.write(env_template)
            
            self.print_success(f"Template créé: {filepath}")
            self.print_warning("⚠️  Modifiez DB_PASSWORD avant de l'uploader!")
            return True
        except Exception as e:
            self.print_error(f"Erreur: {e}")
            return False
    
    def create_wsgi_template(self):
        """Crée un template WSGI"""
        self.print_header("Création du Template WSGI")
        
        username = input("Entrez votre username PythonAnywhere: ").strip()
        
        if not username:
            self.print_error("Username requis!")
            return False
        
        wsgi_template = f"""# WSGI Configuration pour PythonAnywhere
# À copier dans /var/www/{username}_pythonanywhere_com_wsgi.py

import os
import sys

# Ajouter le chemin du projet
path = '/home/{username}/aesi-platform'
if path not in sys.path:
    sys.path.insert(0, path)

# Configurer Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'aesi_platform.settings'

# Indiquer qu'on est sur PythonAnywhere
os.environ['PYTHONANYWHERE_SITE'] = 'True'

# Charger l'application Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
"""
        
        filepath = self.base_dir / "wsgi_pythonanywhere.py"
        
        try:
            with open(filepath, 'w') as f:
                f.write(wsgi_template)
            
            self.print_success(f"Template créé: {filepath}")
            self.print_info(f"À copier dans: /var/www/{username}_pythonanywhere_com_wsgi.py")
            return True
        except Exception as e:
            self.print_error(f"Erreur: {e}")
            return False
    
    def check_settings_mysql(self):
        """Vérifie la configuration MySQL dans settings.py"""
        self.print_header("Vérification de la Configuration MySQL")
        
        settings_file = self.base_dir / "aesi_platform" / "settings.py"
        
        if not settings_file.exists():
            self.print_error(f"Fichier settings.py non trouvé: {settings_file}")
            return False
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifications
        checks = {
            'mysqlclient': "django.db.backends.mysql" in content,
            'decouple': "from decouple import config" in content,
            'DB_NAME': "config('DB_NAME')" in content,
        }
        
        all_ok = True
        for check_name, check_result in checks.items():
            if check_result:
                self.print_success(f"{check_name}: Configuré")
            else:
                self.print_warning(f"{check_name}: Non trouvé")
                all_ok = False
        
        if not all_ok:
            self.print_warning("\nVotre settings.py doit inclure:")
            print("""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
""")
        
        return all_ok
    
    def generate_deployment_checklist(self):
        """Génère une checklist de déploiement"""
        self.print_header("Checklist de Déploiement")
        
        checklist = """
📋 AVANT LE DÉPLOIEMENT (Local)
--------------------------------
[ ] Code fonctionne en local
[ ] requirements_pythonanywhere.txt créé
[ ] .env.pythonanywhere créé et configuré
[ ] wsgi_pythonanywhere.py créé
[ ] settings.py configuré pour MySQL
[ ] Code poussé sur GitHub
[ ] Backup de la base de données locale

🌐 SUR PYTHONANYWHERE
---------------------
[ ] Compte créé
[ ] Console Bash ouverte
[ ] Code cloné: git clone https://github.com/...
[ ] Virtualenv créé: mkvirtualenv --python=/usr/bin/python3.10 aesi-env
[ ] Packages installés: pip install -r requirements_pythonanywhere.txt
[ ] Base MySQL créée (Databases tab)
[ ] Fichier .env créé et configuré
[ ] Web app créée (Web tab)
[ ] WSGI configuré
[ ] Virtualenv path configuré
[ ] Static files mappés:
    [ ] /static/ → /home/username/aesi-platform/staticfiles/
    [ ] /media/ → /home/username/aesi-platform/media/
[ ] Migrations appliquées: python manage.py migrate
[ ] Statiques collectés: python manage.py collectstatic
[ ] Superuser créé: python manage.py createsuperuser
[ ] Dossiers media créés avec permissions
[ ] App rechargée (Reload button)

✅ TESTS POST-DÉPLOIEMENT
-------------------------
[ ] Site accessible: https://username.pythonanywhere.com
[ ] Page d'accueil fonctionne
[ ] Admin accessible: /admin/
[ ] Connexion fonctionne
[ ] Images s'affichent
[ ] CSS chargé (Tailwind)
[ ] Clubs accessibles
[ ] Formulaires fonctionnent
[ ] Pas d'erreur 500
[ ] HTTPS actif (cadenas)
[ ] Logs sans erreur

📝 DOCUMENTATION
---------------
[ ] URL du site notée
[ ] Credentials admin sauvegardés
[ ] Credentials MySQL sauvegardés
[ ] Guide utilisateur préparé
[ ] Plan de maintenance établi
"""
        
        print(checklist)
        
        # Sauvegarder dans un fichier
        filepath = self.base_dir / "CHECKLIST_DEPLOIEMENT.txt"
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(checklist)
            self.print_success(f"Checklist sauvegardée: {filepath}")
        except Exception as e:
            self.print_warning(f"Impossible de sauvegarder: {e}")
    
    def show_menu(self):
        """Affiche le menu principal"""
        self.print_header("🚀 Assistant de Déploiement PythonAnywhere")
        
        menu = """
Choisissez une action:

1. ✅ Vérifier les prérequis
2. 🔑 Générer une SECRET_KEY
3. 📦 Créer requirements_pythonanywhere.txt
4. 📝 Créer template .env
5. 🔧 Créer template WSGI
6. 🔍 Vérifier configuration MySQL
7. 📋 Afficher la checklist de déploiement
8. 🎯 Tout préparer (1-5)
9. 📚 Ouvrir le guide complet
0. ❌ Quitter

"""
        print(menu)
        
        choice = input("Votre choix: ").strip()
        return choice
    
    def prepare_all(self):
        """Prépare tous les fichiers nécessaires"""
        self.print_header("Préparation Complète du Déploiement")
        
        steps = [
            ("Vérification des prérequis", self.check_requirements),
            ("Création requirements", self.create_requirements_pa),
            ("Création template .env", self.create_env_template),
            ("Création template WSGI", self.create_wsgi_template),
            ("Vérification MySQL", self.check_settings_mysql),
        ]
        
        for step_name, step_func in steps:
            self.print_info(f"\n>>> {step_name}...")
            try:
                step_func()
            except Exception as e:
                self.print_error(f"Erreur dans {step_name}: {e}")
        
        self.print_success("\n✅ Préparation terminée!")
        self.print_info("\nProchaines étapes:")
        print("1. Vérifiez les fichiers générés")
        print("2. Modifiez .env.pythonanywhere avec vos credentials")
        print("3. Poussez le code sur GitHub")
        print("4. Suivez le guide: GUIDE_DEPLOIEMENT_PYTHONANYWHERE.md")
    
    def run(self):
        """Lance l'assistant"""
        while True:
            choice = self.show_menu()
            
            if choice == '1':
                self.check_requirements()
            elif choice == '2':
                self.generate_secret_key()
            elif choice == '3':
                self.create_requirements_pa()
            elif choice == '4':
                self.create_env_template()
            elif choice == '5':
                self.create_wsgi_template()
            elif choice == '6':
                self.check_settings_mysql()
            elif choice == '7':
                self.generate_deployment_checklist()
            elif choice == '8':
                self.prepare_all()
            elif choice == '9':
                self.print_info("Consultez: GUIDE_DEPLOIEMENT_PYTHONANYWHERE.md")
            elif choice == '0':
                self.print_success("Au revoir!")
                break
            else:
                self.print_error("Choix invalide")
            
            input("\nAppuyez sur Entrée pour continuer...")


def main():
    """Point d'entrée du script"""
    helper = DeployHelper()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        commands = {
            'check': helper.check_requirements,
            'secret': helper.generate_secret_key,
            'requirements': helper.create_requirements_pa,
            'env': helper.create_env_template,
            'wsgi': helper.create_wsgi_template,
            'mysql': helper.check_settings_mysql,
            'checklist': helper.generate_deployment_checklist,
            'all': helper.prepare_all,
        }
        
        if command in commands:
            commands[command]()
        else:
            helper.print_error(f"Commande inconnue: {command}")
            print("\nCommandes disponibles:")
            for cmd in commands.keys():
                print(f"  - {cmd}")
    else:
        helper.run()


if __name__ == '__main__':
    main()
