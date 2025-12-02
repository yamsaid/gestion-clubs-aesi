"""
Forms for clubs app
"""
from django import forms
from .models import Activity, Club, ActivityPhoto, ActivityResource, Competition, Winner, ActionPlan, Task


class ActivityForm(forms.ModelForm):
    """Form for creating and editing activities"""
    
    class Meta:
        model = Activity
        fields = [
            'title', 'description', 'theme', 'date', 'time', 
            'location', 'status', 'otp_enabled', 'cover_image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Titre de l\'activitÃ©'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Description dÃ©taillÃ©e de l\'activitÃ©',
                'rows': 4
            }),
            'theme': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'ThÃ¨me de l\'activitÃ©'
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'type': 'time'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Lieu de l\'activitÃ©'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent'
            }),
            'otp_enabled': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-300 rounded'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'accept': 'image/*'
            }),
        }
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'theme': 'ThÃ¨me',
            'date': 'Date',
            'time': 'Heure',
            'location': 'Lieu',
            'status': 'Statut',
            'otp_enabled': 'Activer l\'OTP pour cette activitÃ©',
            'cover_image': 'Image de couverture',
        }


class CompleteActivityForm(forms.ModelForm):
    """Form for completing an activity"""
    
    class Meta:
        model = Activity
        fields = ['difficulties']
        widgets = {
            'difficulties': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'DÃ©crivez les difficultÃ©s rencontrÃ©es (optionnel)...',
                'rows': 4
            }),
        }
        labels = {
            'difficulties': 'DifficultÃ©s rencontrÃ©es',
        }


class CancelActivityForm(forms.ModelForm):
    """Form for cancelling an activity"""
    
    class Meta:
        model = Activity
        fields = ['cancellation_comment']
        widgets = {
            'cancellation_comment': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-red-500 focus:border-transparent',
                'placeholder': 'Expliquez les raisons de l\'annulation...',
                'rows': 4
            }),
        }
        labels = {
            'cancellation_comment': 'Raison de l\'annulation',
        }
    
    def clean_cancellation_comment(self):
        comment = self.cleaned_data.get('cancellation_comment')
        if not comment or len(comment.strip()) < 10:
            raise forms.ValidationError('Veuillez fournir une raison dÃ©taillÃ©e (au moins 10 caractÃ¨res).')
        return comment


class ActivityPhotoForm(forms.ModelForm):
    """Form for adding photos to an activity"""
    
    class Meta:
        model = ActivityPhoto
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'LÃ©gende de la photo (optionnel)'
            }),
        }
        labels = {
            'image': 'Photo',
            'caption': 'LÃ©gende',
        }


class ActivityResourceForm(forms.ModelForm):
    """Form for adding resources to an activity"""
    
    class Meta:
        model = ActivityResource
        fields = ['title', 'description', 'file', 'resource_type']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Titre du document'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Description (optionnel)',
                'rows': 3
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.rar'
            }),
            'resource_type': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent'
            }),
        }
        labels = {
            'title': 'Titre',
            'description': 'Description',
            'file': 'Fichier',
            'resource_type': 'Type de ressource',
        }


class CompetitionForm(forms.ModelForm):
    """Form for creating competitions"""
    
    class Meta:
        model = Competition
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Nom de la compÃ©tition'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Description (optionnel)',
                'rows': 3
            }),
        }
        labels = {
            'name': 'Nom',
            'description': 'Description',
        }


class WinnerForm(forms.ModelForm):
    """Form for adding winners"""
    
    class Meta:
        model = Winner
        fields = ['participant', 'rank', 'prize']
        widgets = {
            'participant': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent'
            }),
            'rank': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Rang (1, 2, 3...)',
                'min': '1'
            }),
            'prize': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Prix ou rÃ©compense (optionnel)'
            }),
        }
        labels = {
            'participant': 'Participant',
            'rank': 'Rang',
            'prize': 'Prix',
        }


class ActionPlanForm(forms.ModelForm):
    """Form for creating/editing action plans (programmes)"""
    
    class Meta:
        model = ActionPlan
        fields = ['title', 'description', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary',
                'placeholder': 'Titre du programme'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary',
                'rows': 4,
                'placeholder': 'Description du programme'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary',
                'type': 'date'
            })
        }


class TaskForm(forms.ModelForm):
    """Form for creating/editing tasks"""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary',
                'placeholder': 'Titre de la tÃ¢che'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary',
                'rows': 3,
                'placeholder': 'Description de la tÃ¢che'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-primary focus:border-primary',
                'type': 'date'
            })
        }
    
    def __init__(self, *args, club=None, **kwargs):
        super().__init__(*args, **kwargs)
        if club:
            from clubs.models import ClubMember
            self.fields['assigned_to'].queryset = ClubMember.objects.filter(club=club, is_active=True)
        self.fields['assigned_to'].required = False

