"""
Models for participation app
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from core.models import TimeStampedModel


class Participation(TimeStampedModel):
    """Model for activity participation"""
    
    activity = models.ForeignKey(
        'clubs.Activity',
        on_delete=models.CASCADE,
        related_name='participations',
        verbose_name=_('activité')
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='participations',
        verbose_name=_('participant')
    )
    
    # OTP verification
    otp_verified = models.BooleanField(_('OTP vérifié'), default=False)
    otp_verified_at = models.DateTimeField(_('OTP vérifié le'), null=True, blank=True)
    
    # Participant feedback
    appreciation = models.TextField(_('appréciation'), blank=True)
    suggestion = models.TextField(_('suggestion'), blank=True)
    rating = models.IntegerField(
        _('note'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text=_('Note de 1 à 5')
    )
    
    # Photos uploaded by participant
    photo1 = models.ImageField(
        _('photo 1'),
        upload_to='participation/photos/',
        blank=True,
        null=True
    )
    photo2 = models.ImageField(
        _('photo 2'),
        upload_to='participation/photos/',
        blank=True,
        null=True
    )
    photo3 = models.ImageField(
        _('photo 3'),
        upload_to='participation/photos/',
        blank=True,
        null=True
    )
    
    # Track submission
    submitted_at = models.DateTimeField(_('soumis le'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('participation')
        verbose_name_plural = _('participations')
        ordering = ['-created_at']
        unique_together = ['activity', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.activity.title}"
    
    @property
    def is_completed(self):
        """Check if participation form is completed"""
        return self.otp_verified and self.submitted_at is not None
    
    @property
    def attendance_rate(self):
        """Calculate attendance rate for this user across all activities"""
        total_activities = self.user.participations.filter(otp_verified=True).count()
        return total_activities


class ParticipationStats(models.Model):
    """Model for caching participation statistics"""
    
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='participation_stats',
        verbose_name=_('utilisateur')
    )
    
    # Overall stats
    total_participations = models.IntegerField(_('total participations'), default=0)
    average_rating = models.FloatField(_('note moyenne'), default=0.0)
    
    # Per club stats
    informatique_count = models.IntegerField(_('participations informatique'), default=0)
    anglais_count = models.IntegerField(_('participations anglais'), default=0)
    art_oratoire_count = models.IntegerField(_('participations art oratoire'), default=0)
    sport_count = models.IntegerField(_('participations sport'), default=0)
    
    # Achievements
    total_wins = models.IntegerField(_('total victoires'), default=0)
    
    # Last updated
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('statistique de participation')
        verbose_name_plural = _('statistiques de participation')
    
    def __str__(self):
        return f"Stats - {self.user.get_full_name()}"
    
    def update_stats(self):
        """Update participation statistics"""
        from clubs.models import Club, Winner
        
        participations = self.user.participations.filter(otp_verified=True)
        
        self.total_participations = participations.count()
        
        # Calculate average rating
        ratings = participations.exclude(rating__isnull=True).values_list('rating', flat=True)
        if ratings:
            self.average_rating = sum(ratings) / len(ratings)
        
        # Count per club type
        self.informatique_count = participations.filter(
            activity__club__type='INFORMATIQUE'
        ).count()
        self.anglais_count = participations.filter(
            activity__club__type='ANGLAIS'
        ).count()
        self.art_oratoire_count = participations.filter(
            activity__club__type='ART_ORATOIRE'
        ).count()
        self.sport_count = participations.filter(
            activity__club__type='SPORT'
        ).count()
        
        # Count wins
        self.total_wins = Winner.objects.filter(participant=self.user).count()
        
        self.save()


class DynamicParticipationForm(TimeStampedModel):
    """Model for dynamically generated participation forms"""
    
    activity = models.OneToOneField(
        'clubs.Activity',
        on_delete=models.CASCADE,
        related_name='dynamic_form',
        verbose_name=_('activité')
    )
    
    # Form creator (organizer)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='created_forms',
        verbose_name=_('créé par')
    )
    
    # OTP for form access
    otp_code = models.CharField(_('code OTP'), max_length=6)
    otp_generated_at = models.DateTimeField(_('OTP généré le'), auto_now_add=True)
    otp_expires_at = models.DateTimeField(_('OTP expire le'))
    
    # Form link
    form_link = models.CharField(_('lien du formulaire'), max_length=255, unique=True)
    
    # Form status
    is_active = models.BooleanField(_('actif'), default=True)
    
    # Statistics
    access_count = models.IntegerField(_('nombre d\'accès'), default=0)
    submission_count = models.IntegerField(_('nombre de soumissions'), default=0)
    
    class Meta:
        verbose_name = _('formulaire de participation dynamique')
        verbose_name_plural = _('formulaires de participation dynamiques')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Formulaire - {self.activity.title}"
    
    def is_expired(self):
        """Check if OTP is expired"""
        from django.utils import timezone
        return timezone.now() > self.otp_expires_at
    
    def increment_access(self):
        """Increment access count"""
        self.access_count += 1
        self.save(update_fields=['access_count'])
    
    def increment_submission(self):
        """Increment submission count"""
        self.submission_count += 1
        self.save(update_fields=['submission_count'])
