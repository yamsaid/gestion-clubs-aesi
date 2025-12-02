"""
User models for AESI platform
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'adresse email doit être fournie'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'AESI_EXECUTIVE')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser doit avoir is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser doit avoir is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with role-based access"""
    
    ROLE_CHOICES = [
        ('STUDENT', 'Étudiant'),
        ('CLUB_EXECUTIVE', 'Membre exécutif du club'),
        ('AESI_TREASURER', 'Trésorier de l\'AESI'),
    ]
    
    FILIERE_CHOICES = [
        ('IDA', 'Ingénieur d\'Application'),
        ('ITS', 'Ingénieur Travaux Statistiques'),
        ('TSE', 'Technicien Supérieur d\'Économie'),
        ('TS', 'Technicien Supérieur de la Statistique'),
        ('AT', 'Agent Technique de la Statistique'),
    ]
    
    NIVEAU_CHOICES = [
        ('1', '1ère année'),
        ('2', '2ème année'),
        ('3', '3ème année'),
        ('4', '4ème année'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    username = None  # Remove username field
    email = models.EmailField(_('adresse email'), unique=True)
    first_name = models.CharField(_('prénom'), max_length=150)
    last_name = models.CharField(_('nom'), max_length=150)
    
    role = models.CharField(
        _('rôle'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='STUDENT'
    )
    
    # Student information
    gender = models.CharField(
        _('sexe'),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True
    )
    filiere = models.CharField(
        _('filière'),
        max_length=10,
        choices=FILIERE_CHOICES,
        blank=True
    )
    niveau = models.CharField(
        _('niveau'),
        max_length=2,
        choices=NIVEAU_CHOICES,
        blank=True
    )
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    
    # Profile
    profile_picture = models.ImageField(
        _('photo de profil'),
        upload_to='profiles/',
        blank=True,
        null=True
    )
    bio = models.TextField(_('biographie'), blank=True)
    
    # Two-factor authentication
    two_factor_enabled = models.BooleanField(_('authentification à deux facteurs'), default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_club_executive(self):
        """Check if user is a club executive"""
        return self.role == 'CLUB_EXECUTIVE'
    
    @property
    def is_aesi_treasurer(self):
        """Check if user is AESI treasurer"""
        return self.role == 'AESI_TREASURER'
    
    @property
    def is_student(self):
        """Check if user is a student"""
        return self.role == 'STUDENT'
    
    def get_user_club(self):
        """
        Get the club this user is a member of (if any)
        Returns: Club object or None
        """
        from clubs.models import ClubMember
        try:
            # Get club member - ClubMember uses OneToOneField so we can use club_member directly
            club_member = ClubMember.objects.filter(
                user=self,
                is_active=True,
                position__in=['PRESIDENT', 'VICE_PRESIDENT', 'SECRETARY', 'TREASURER', 'COMMUNICATION']
            ).first()
            return club_member.club if club_member else None
        except:
            return None
    
    def can_manage_club(self, club):
        """
        Check if user can manage a specific club
        
        Rules:
        - Étudiant: NO
        - Membre exécutif du club: YES only for their club
        - Trésorier AESI: NO (read-only access)
        - Staff: YES for all clubs
        """
        # Staff can manage all clubs
        if self.is_staff:
            return True
        
        # Treasurer cannot manage clubs
        if self.is_aesi_treasurer:
            return False
        
        # Club executives can only manage their own club
        if self.is_club_executive:
            user_club = self.get_user_club()
            if user_club and club:
                return user_club.id == club.id
        
        # Students cannot manage
        return False
    
    def can_view_finances(self, club=None):
        """
        Check if user can view financial data
        
        Rules:
        - Étudiant: NO
        - Membre exécutif du club: YES only for their club
        - Trésorier AESI: YES for ALL clubs
        - Staff: YES for all clubs
        """
        # Staff can view all finances
        if self.is_staff:
            return True
        
        # Treasurer can view all finances
        if self.is_aesi_treasurer:
            return True
        
        # Club executives can only view their own club's finances
        if self.is_club_executive:
            if club is None:
                return False
            user_club = self.get_user_club()
            if user_club:
                return user_club.id == club.id
        
        # Students cannot view finances
        return False
    
    def can_modify_finances(self, club=None):
        """
        Check if user can modify financial data
        
        Rules:
        - Étudiant: NO
        - Membre exécutif du club: YES only for their club
        - Trésorier AESI: NO (read-only)
        - Staff: YES for all clubs
        """
        # Staff can modify all finances
        if self.is_staff:
            return True
        
        # Treasurer CANNOT modify (read-only)
        if self.is_aesi_treasurer:
            return False
        
        # Club executives can only modify their own club's finances
        if self.is_club_executive:
            if club is None:
                return False
            user_club = self.get_user_club()
            if user_club:
                return user_club.id == club.id
        
        # Students cannot modify finances
        return False
    
    def get_attendance_rate(self, club=None):
        """Calculate attendance rate for this user"""
        from participation.models import Participation
        
        participations = Participation.objects.filter(
            user=self,
            otp_verified=True
        )
        
        if club:
            participations = participations.filter(activity__club=club)
        
        return participations.count()
    
    def get_attendance_percentage(self, club=None):
        """Calculate attendance percentage based on total activities"""
        from clubs.models import Activity
        
        # Get total completed activities
        total_activities_query = Activity.objects.filter(status='COMPLETED')
        
        if club:
            total_activities_query = total_activities_query.filter(club=club)
        
        total_activities = total_activities_query.count()
        
        if total_activities == 0:
            return 0
        
        attended = self.get_attendance_rate(club)
        return round((attended / total_activities) * 100, 2)
