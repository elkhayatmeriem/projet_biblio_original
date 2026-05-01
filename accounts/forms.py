import re
from django import forms
from django.core.exceptions import ValidationError

class RegisterForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not password:
            return password

        if len(password) < 8:
            raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")

        if not re.search(r'[A-Z]', password):
            raise ValidationError("Ajoute au moins une majuscule.")

        if not re.search(r'[a-z]', password):
            raise ValidationError("Ajoute au moins une minuscule.")

        if not re.search(r'\d', password):
            raise ValidationError("Ajoute au moins un chiffre.")

        if not re.search(r'[!@#$%^&*(),.?\":{}|<>_]', password):
            raise ValidationError("Ajoute un caractère spécial.")

        if " " in password:
            raise ValidationError("Le mot de passe ne doit pas contenir d'espaces.")

        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            raise ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data