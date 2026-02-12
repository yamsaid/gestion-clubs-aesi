"""
Models for clubs app
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import TimeStampedModel, AuditModel


class Club(TimeStampedModel):
    """Model representing a club"""
    
    CLUB_TYPES = [
        ('INFORMATIQUE', 'Club d\'Informatique'),
        ('ANGLAIS', 'Club d\'Anglais'),
        ('ART_ORATOIRE', 'Club d\'Art Oratoire'),
        ('SPORT', 'Club de Sport'),
    ]
    
    name = models.CharField(_('nom'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), unique=True)
    type = models.CharField(_('type'), max_length=20, choices=CLUB_TYPES)
    description = models.TextField(_('description'))
    logo = models.ImageField(_('logo'), upload_to='clubs/logos/', blank=True, null=True)
    cover_image = models.ImageField(_('image de couverture'), upload_to='clubs/covers/', blank=True, null=True)
    
    # Contact information
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    
    # Social media
    facebook_url = models.URLField(_('Facebook'), blank=True)
    twitter_url = models.URLField(_('Twitter'), blank=True)
    instagram_url = models.URLField(_('Instagram'), blank=True)
    
    is_active = models.BooleanField(_('actif'), default=True)
    
    class Meta:
        verbose_name = _('club')
        verbose_name_plural = _('clubs')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def execution_rate(self):
        """Calculate execution rate based on completed tasks"""
        total_tasks = self.action_plans.aggregate(
            total=models.Count('tasks')
        )['total'] or 0
        
        if total_tasks == 0:
            return 0
        
        completed_tasks = self.action_plans.aggregate(
            completed=models.Count('tasks', filter=models.Q(tasks__is_completed=True))
        )['completed'] or 0
        
        return round((completed_tasks / total_tasks) * 100, 2)


class ClubMember(AuditModel):
    """Model representing a club executive member"""
    
    POSITION_CHOICES = [
        ('PRESIDENT', 'Coordonateur(trice)'),
        ('SECRETARY', 'Secrétaire'),
        ('TREASURER', 'Trésorier(ère)'),
        ('COMMUNICATION', 'Organisateur(trice)'),
        ('MEMBER', 'Membre'),
    ]
    
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_('club')
    )
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='club_member',
        verbose_name=_('utilisateur')
    )
    position = models.CharField(
        _('poste'),
        max_length=20,
        choices=POSITION_CHOICES
    )
    missions = models.TextField(
        _('missions spécifiques'),
        blank=True,
        help_text=_('Décrivez les missions et responsabilités spécifiques de ce membre')
    )
    start_date = models.DateField(_('date de début'))
    end_date = models.DateField(_('date de fin'), blank=True, null=True)
    is_active = models.BooleanField(_('actif'), default=True)
    
    class Meta:
        verbose_name = _('membre exécutif')
        verbose_name_plural = _('membres exécutifs')
        ordering = ['-start_date']
        unique_together = ['club', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.club.name} ({self.get_position_display()})"


class ActionPlan(AuditModel):
    """Model for club action plans"""
    
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='action_plans',
        verbose_name=_('club')
    )
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    start_date = models.DateField(_('date de début'))
    end_date = models.DateField(_('date de fin'))
    
    class Meta:
        verbose_name = _('programme d\'action')
        verbose_name_plural = _('programmes d\'action')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.club.name} - {self.title}"
    
    @property
    def completion_rate(self):
        """Calculate completion rate"""
        total = self.tasks.count()
        if total == 0:
            return 0
        completed = self.tasks.filter(is_completed=True).count()
        return round((completed / total) * 100, 2)


class Task(AuditModel):
    """Model for tasks within action plans"""
    
    action_plan = models.ForeignKey(
        ActionPlan,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('programme d\'action')
    )
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    assigned_to = models.ForeignKey(
        ClubMember,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name=_('assigné à')
    )
    due_date = models.DateField(_('date limite'))
    is_completed = models.BooleanField(_('complété'), default=False)
    completed_at = models.DateTimeField(_('complété le'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('tâche')
        verbose_name_plural = _('tâches')
        ordering = ['due_date']
    
    def __str__(self):
        return self.title


class Activity(AuditModel):
    """Model for club activities"""
    
    STATUS_CHOICES = [
        ('PLANNED', 'Planifiée'),
        ('ONGOING', 'En cours'),
        ('COMPLETED', 'Terminée'),
        ('CANCELLED', 'Annulée'),
    ]
    
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('club')
    )
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'))
    theme = models.CharField(_('thème'), max_length=200)
    
    # Date and location
    date = models.DateField(_('date'))
    time = models.TimeField(_('heure'), blank=True, null=True)
    location = models.CharField(_('lieu'), max_length=200)
    
    # Status
    status = models.CharField(
        _('statut'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='PLANNED'
    )
    
    # OTP for participation
    otp_enabled = models.BooleanField(_('OTP activé'), default=True)
    
    # Difficulties and feedback (for completed activities)
    difficulties = models.TextField(_('difficultés rencontrées'), blank=True)
    
    # Cancellation comment (for cancelled activities)
    cancellation_comment = models.TextField(_('commentaire d\'annulation'), blank=True)
    cancellation_date = models.DateTimeField(_('date d\'annulation'), blank=True, null=True)
    
    # Completion date
    completion_date = models.DateTimeField(_('date de complétion'), blank=True, null=True)
    
    # Cover image
    cover_image = models.ImageField(
        _('image de couverture'),
        upload_to='activities/covers/',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('activité')
        verbose_name_plural = _('activités')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.club.name} - {self.title}"
    
    @property
    def participants_count(self):
        """Get number of participants"""
        return self.participations.count()


class ActivityPhoto(TimeStampedModel):
    """Model for activity photos"""
    
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name=_('activité')
    )
    image = models.ImageField(_('image'), upload_to='activities/photos/')
    caption = models.CharField(_('légende'), max_length=200, blank=True)
    uploaded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('téléchargé par')
    )
    
    class Meta:
        verbose_name = _('photo d\'activité')
        verbose_name_plural = _('photos d\'activités')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Photo - {self.activity.title}"


class Competition(AuditModel):
    """Model for competitions within activities"""
    
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='competitions',
        verbose_name=_('activité')
    )
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('compétition')
        verbose_name_plural = _('compétitions')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.activity.title} - {self.name}"


class Winner(TimeStampedModel):
    """Model for competition winners"""
    
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='winners',
        verbose_name=_('compétition')
    )
    participant = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='wins',
        verbose_name=_('participant')
    )
    rank = models.IntegerField(
        _('rang'),
        validators=[MinValueValidator(1)]
    )
    prize = models.CharField(_('prix'), max_length=200, blank=True)
    
    class Meta:
        verbose_name = _('gagnant')
        verbose_name_plural = _('gagnants')
        ordering = ['rank']
        unique_together = ['competition', 'rank']
    
    def __str__(self):
        return f"{self.participant.get_full_name()} - Rang {self.rank}"


class ActivityResource(TimeStampedModel):
    """Model for activity resources (documents, files, etc.)"""
    
    RESOURCE_TYPES = [
        ('PDF', 'Document PDF'),
        ('DOC', 'Document Word'),
        ('XLS', 'Document Excel'),
        ('PPT', 'Présentation PowerPoint'),
        ('ZIP', 'Archive ZIP'),
        ('OTHER', 'Autre'),
    ]
    
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name=_('activité')
    )
    title = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    file = models.FileField(
        _('fichier'),
        upload_to='activities/resources/',
        help_text=_('PDF, Word, Excel, PowerPoint, ZIP, etc.')
    )
    resource_type = models.CharField(
        _('type de ressource'),
        max_length=20,
        choices=RESOURCE_TYPES,
        default='OTHER'
    )
    uploaded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('téléchargé par')
    )
    
    class Meta:
        verbose_name = _('ressource d\'activité')
        verbose_name_plural = _('ressources d\'activités')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.activity.title}"
    
    @property
    def file_extension(self):
        """Get file extension"""
        import os
        return os.path.splitext(self.file.name)[1].lower()


class MemberAttendance(TimeStampedModel):
    """Model for tracking executive member attendance"""
    
    member = models.ForeignKey(
        ClubMember,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('membre')
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='member_attendances',
        verbose_name=_('activité')
    )
    is_present = models.BooleanField(_('présent'), default=False)
    marked_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('marqué par')
    )
    notes = models.TextField(_('notes'), blank=True)
    
    class Meta:
        verbose_name = _('assiduité membre')
        verbose_name_plural = _('assiduités membres')
        ordering = ['-created_at']
        unique_together = ['member', 'activity']
    
    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.activity.title}"
