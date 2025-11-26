"""
Custom allauth adapters for user management
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to handle additional user fields during signup
    """
    
    def save_user(self, request, user, form, commit=True):
        """
        Save user with additional fields from the signup form
        """
        # Save default fields (email)
        user = super().save_user(request, user, form, commit=False)
        
        # Get data from POST request since form might not have our custom fields
        data = request.POST
        
        # Set additional fields from POST data
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')
        user.phone = data.get('phone', '')
        user.gender = data.get('gender', '')
        user.filiere = data.get('filiere', '')
        user.niveau = data.get('niveau', '')
        user.role = 'STUDENT'  # Default role for new signups
        
        if commit:
            user.save()
        
        return user
    
    def get_signup_form_class(self, request):
        """
        Return custom signup form with additional fields
        """
        from users.models import User
        
        # Classes CSS communes pour tous les champs
        input_classes = 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition sm:text-sm'
        select_classes = 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition sm:text-sm appearance-none'
        
        class CustomSignupForm(AllauthSignupForm):
            """Extended signup form with additional fields"""
            
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
                    'class': input_classes,
                    'placeholder': 'exemple@issp.bj'
                })
                self.fields['password1'].widget.attrs.update({
                    'class': input_classes,
                    'placeholder': '••••••••'
                })
                self.fields['password2'].widget.attrs.update({
                    'class': input_classes,
                    'placeholder': '••••••••'
                })
            
            field_order = ['first_name', 'last_name', 'email', 'phone', 'gender', 'filiere', 'niveau', 'password1', 'password2']
        
        return CustomSignupForm
