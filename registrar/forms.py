from django import forms
from .models import Patient, Address, Appointments
import re
from django.core.exceptions import ValidationError

# Method to validate name field
def validate_name(value):
    # Define the regex pattern for the name field (supports slashes, spaces, apostrophes, etc.)
    name_regex = r"^[A-Za-zÀ-ÿ/ '-]+$"
    
    # Check if the name matches the regex pattern
    if not re.match(name_regex, value):
        raise ValidationError("Invalid name format. Name can only contain letters, slashes (/), spaces, apostrophes ('), and hyphens (-).")

# Method to validate phone number field (Ethiopian phone number format: +2519XXXXXXXX)
def validate_phone_number(value):
    # Define the regex pattern for Ethiopian phone numbers
    phone_regex = r"^(?:0|\+251)\d{9}$"
    
    # Check if the phone number matches the regex pattern
    if not re.match(phone_regex, value):
        raise ValidationError("phone number contains error")

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointments
        fields = ['reason', 'date']
    
        widgets = {
            'date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={"class" : "form-control", 'rows': 5, 'placeholder': 'Reason'}),
        }
    
    def clean_reason(self):
        if not self.cleaned_data.get('reason'):
            raise forms.ValidationError('Reason is required')
        # further validation
        return self.cleaned_data.get('reason')

    def clean_date(self):
        if not self.cleaned_data.get('date'):
            raise forms.ValidationError('date is required')
        # further validation
        return self.cleaned_data.get('date')


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['region', 'zone', 'woreda', 'kebele', 'ketena', 'house_no']
        
        widgets = {
            'region': forms.Select(attrs={'class': 'form-control', 'id': 'region', 'placeholder': "---choose region---"}),
            'kebele': forms.TextInput(attrs={'class': 'form-control'}),
            'ketena': forms.TextInput(attrs={'class': 'form-control'}),
            'house_no': forms.TextInput(attrs={'class': 'form-control'}),
            'zone': forms.Select(attrs={'class': 'form-control', 'id': 'id_zone', 'disabled': 'disabled'}),
            'woreda': forms.Select(attrs={'class': 'form-control', 'id': 'id_woreda', 'disabled': 'disabled'}),
        }
    

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'middle_name', 'last_name', 'age', 'gender', 'phone', 'national_id']
        
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),  # Custom widget for gender
            'age': forms.TextInput(attrs={'type': 'number', 'class': 'form-control', 'id': 'age',}),  # Date Picker for DOB
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),  # Text Input for First Name
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Phone'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control',}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Middle Name'}),  # Text Input for Middle Name
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),  # Text Input for Last Name
        }
    # Validation for fields
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if not age:
            raise forms.ValidationError('Age is required')
        elif age < 0 and age > 150:
            raise forms.ValidationError('Age value is not correct')
        return age
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError('First Name is required.')
        else:
            validate_name(first_name)
        return first_name

    def clean_middle_name(self):
        middle_name = self.cleaned_data.get('middle_name')
        if not middle_name:
            raise forms.ValidationError('Middle Name is required')
        else:
            validate_name(middle_name)
        return middle_name  # You can add validation if needed (e.g., optional field)

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError('Last Name is required.')
        else:
            validate_name(last_name)
        return last_name

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise forms.ValidationError('Gender is required.')
        return gender

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required")
        elif len(phone) < 10 or len(phone) > 13:
            raise forms.ValidationError('Phone number must be at least 10 or 13 digits.')
        else:
            validate_phone_number(phone)
        return phone

    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if not national_id or len(national_id) < 12:
            raise forms.ValidationError('National ID must be at least 12 digits.')
        return national_id

