from django import forms
from .models import User

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'gender']
        widgets = {
            'password': forms.PasswordInput(),  # Ensure the password field is rendered as a password input
        }

    def save(self, commit=True):
        """
        Override the save method to handle password hashing.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()
        return user
    
    
    
