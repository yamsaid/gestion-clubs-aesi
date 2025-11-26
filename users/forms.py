"""
Forms for users app
"""
from django import forms
from allauth.account.forms import SignupForm
from .models import User


class CustomSignupForm(SignupForm):
    """Extended signup form with additional fields"""
    
    # Classes CSS communes pour tous les champs
    input_classes = 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition sm:text-sm'
    select_classes = 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition sm:text-sm appearance-none'
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Prénom',
        widget=forms.TextInput(attrs={
            'placeholder': 'Jean',
            'class': input_classes,
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nom',
        widget=forms.TextInput(attrs={
            'placeholder': 'Dupont',
            'class': input_classes,
        })
    )
    
    gender = forms.ChoiceField(
        choices=[('', 'Sélectionner')] + list(User.GENDER_CHOICES),
        required=False,
        label='Sexe',
        widget=forms.Select(attrs={
            'class': select_classes,
        })
    )
    
    filiere = forms.ChoiceField(
        choices=[('', 'Sélectionner une filière')] + list(User.FILIERE_CHOICES),
        required=False,
        label='Filière',
        widget=forms.Select(attrs={
            'class': select_classes,
        })
    )
    
    niveau = forms.ChoiceField(
        choices=[('', 'Sélectionner un niveau')] + list(User.NIVEAU_CHOICES),
        required=False,
        label='Niveau',
        widget=forms.Select(attrs={
            'class': select_classes,
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        label='Téléphone',
        widget=forms.TextInput(attrs={
            'placeholder': '+229 XX XX XX XX',
            'class': input_classes,
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter les classes CSS aux champs email et password d'allauth
        self.fields['email'].widget.attrs.update({
            'class': self.input_classes,
            'placeholder': 'exemple@issp.bj'
        })
        self.fields['password1'].widget.attrs.update({
            'class': self.input_classes,
            'placeholder': '••••••••'
        })
        self.fields['password2'].widget.attrs.update({
            'class': self.input_classes,
            'placeholder': '••••••••'
        })
    
    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.gender = self.cleaned_data.get('gender', '')
        user.filiere = self.cleaned_data.get('filiere', '')
        user.niveau = self.cleaned_data.get('niveau', '')
        user.role = 'STUDENT'  # Default role for new signups
        user.save()
        return user
    
    field_order = ['first_name', 'last_name', 'email', 'phone', 'gender', 'filiere', 'niveau', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'filiere', 
                  'niveau', 'profile_picture', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
