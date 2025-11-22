"""
Admin configuration for participation app
"""
from django.contrib import admin
from .models import Participation, ParticipationStats


@admin.register(Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'activity', 'otp_verified', 'rating',
        'submitted_at', 'created_at'
    ]
    list_filter = [
        'otp_verified', 'activity__club', 'rating', 'created_at'
    ]
    search_fields = [
        'user__first_name', 'user__last_name',
        'user__email', 'activity__title'
    ]
    readonly_fields = ['created_at', 'otp_verified_at', 'submitted_at']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('activity', 'user')
        }),
        ('Vérification OTP', {
            'fields': ('otp_verified', 'otp_verified_at')
        }),
        ('Feedback', {
            'fields': ('appreciation', 'suggestion', 'rating')
        }),
        ('Photos', {
            'fields': ('photo1', 'photo2', 'photo3')
        }),
        ('Dates', {
            'fields': ('submitted_at', 'created_at')
        }),
    )


@admin.register(ParticipationStats)
class ParticipationStatsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'total_participations', 'average_rating',
        'total_wins', 'updated_at'
    ]
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['updated_at']
    
    actions = ['update_stats']
    
    def update_stats(self, request, queryset):
        """Action to update stats for selected users"""
        count = 0
        for stats in queryset:
            stats.update_stats()
            count += 1
        self.message_user(
            request,
            f'{count} statistiques mises à jour avec succès.'
        )
    update_stats.short_description = "Mettre à jour les statistiques"
