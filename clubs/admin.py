"""
Admin configuration for clubs app
"""
from django.contrib import admin
from .models import (
    Club, ClubMember, ActionPlan, Task, Activity,
    ActivityPhoto, ActivityResource, Competition, Winner, MemberAttendance
)


class ClubMemberInline(admin.TabularInline):
    model = ClubMember
    extra = 1
    fields = ['user', 'position', 'start_date', 'end_date', 'is_active']


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_active', 'created_at']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ClubMemberInline]


@admin.register(ClubMember)
class ClubMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'club', 'position', 'start_date', 'is_active']
    list_filter = ['club', 'position', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ['title', 'assigned_to', 'due_date', 'is_completed']


@admin.register(ActionPlan)
class ActionPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'club', 'start_date', 'end_date', 'completion_rate']
    list_filter = ['club', 'start_date']
    search_fields = ['title', 'description']
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'action_plan', 'assigned_to', 'due_date', 'is_completed']
    list_filter = ['is_completed', 'due_date']
    search_fields = ['title', 'description']


class ActivityPhotoInline(admin.TabularInline):
    model = ActivityPhoto
    extra = 1
    fields = ['image', 'caption', 'uploaded_by']


class ActivityResourceInline(admin.TabularInline):
    model = ActivityResource
    extra = 1
    fields = ['title', 'resource_type', 'file', 'uploaded_by']


class CompetitionInline(admin.TabularInline):
    model = Competition
    extra = 0


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'club', 'date', 'status', 'participants_count', 'otp_enabled']
    list_filter = ['club', 'status', 'date']
    search_fields = ['title', 'description', 'theme']
    inlines = [ActivityPhotoInline, ActivityResourceInline, CompetitionInline]
    fieldsets = (
        ('Informations générales', {
            'fields': ('club', 'title', 'description', 'theme', 'cover_image')
        }),
        ('Date et lieu', {
            'fields': ('date', 'time', 'location')
        }),
        ('Statut', {
            'fields': ('status', 'otp_enabled')
        }),
        ('Complétion', {
            'fields': ('difficulties', 'completion_date'),
            'classes': ('collapse',)
        }),
        ('Annulation', {
            'fields': ('cancellation_comment', 'cancellation_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ActivityPhoto)
class ActivityPhotoAdmin(admin.ModelAdmin):
    list_display = ['activity', 'caption', 'uploaded_by', 'created_at']
    list_filter = ['activity__club', 'created_at']
    search_fields = ['caption', 'activity__title']


@admin.register(ActivityResource)
class ActivityResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'activity', 'resource_type', 'uploaded_by', 'created_at']
    list_filter = ['activity__club', 'resource_type', 'created_at']
    search_fields = ['title', 'description', 'activity__title']


class WinnerInline(admin.TabularInline):
    model = Winner
    extra = 1
    fields = ['participant', 'rank', 'prize']


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'activity', 'created_at']
    list_filter = ['activity__club']
    search_fields = ['name', 'description']
    inlines = [WinnerInline]


@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ['participant', 'competition', 'rank', 'prize']
    list_filter = ['competition__activity__club', 'rank']
    search_fields = ['participant__first_name', 'participant__last_name']


@admin.register(MemberAttendance)
class MemberAttendanceAdmin(admin.ModelAdmin):
    list_display = ['member', 'activity', 'is_present', 'marked_by', 'created_at']
    list_filter = ['is_present', 'activity__club', 'created_at']
    search_fields = ['member__user__first_name', 'member__user__last_name']
