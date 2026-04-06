from django import forms
from django.contrib.auth.hashers import make_password
from .models import Staff  # Import your user model

class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not Staff.objects.filter(username=username).exists():
            raise forms.ValidationError("This username does not exist.")
        return username

    def clean_password(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = Staff.objects.filter(username=username).first()
        if user and not user.check_password(password):
            raise forms.ValidationError("Incorrect password.")
        return password
    
class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Staff
        fields = ['username', 'email', 'password', 'role', 'department']  # Add necessary fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])  # Encrypt password
        if commit:
            user.save()
        return user