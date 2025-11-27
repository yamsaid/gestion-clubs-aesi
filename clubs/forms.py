"""
Forms for clubs app
"""
from django import forms
from .models import Activity, Club


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
                'placeholder': 'Titre de l\'activité'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Description détaillée de l\'activité',
                'rows': 4
            }),
            'theme': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Thème de l\'activité'
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
                'placeholder': 'Lieu de l\'activité'
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
            'theme': 'Thème',
            'date': 'Date',
            'time': 'Heure',
            'location': 'Lieu',
            'status': 'Statut',
            'otp_enabled': 'Activer l\'OTP pour cette activité',
            'cover_image': 'Image de couverture',
        }
