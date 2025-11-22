"""
Forms for participation app
"""
from django import forms
from .models import Participation


class ParticipationForm(forms.ModelForm):
    """Form for participant feedback"""
    
    class Meta:
        model = Participation
        fields = [
            'appreciation', 'suggestion', 'rating',
            'photo1', 'photo2', 'photo3'
        ]
        widgets = {
            'appreciation': forms.Textarea(attrs={'rows': 4}),
            'suggestion': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
        }
