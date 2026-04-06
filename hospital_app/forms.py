from .models import TriageRecord, Visit, SystemExamination, LabTestRequest, LabTest, LabTestResult
from django import forms
import re

class LabTestRequestForm(forms.ModelForm):
    """Form for doctors to request lab tests."""
    tests = forms.ModelMultipleChoiceField(
        queryset=LabTest.objects.all(),
        widget=forms.SelectMultiple,  # Dropdown with multi-select functionality
        required=True,
        label="Select Tests", 
    )

    class Meta:
        model = LabTestRequest
        fields = ['visit', 'tests', 'notes']
        widgets = {
            'visit': forms.HiddenInput(),  # Auto-fill visit ID
            'notes': forms.Textarea(attrs={'"class" : "form-control", rows': 3, 'placeholder': 'Additional instructions (optional)'}),
        }


class LabTestResultForm(forms.ModelForm):
    """Form for lab technicians to enter test results."""
    
    class Meta:
        model = LabTestResult
        fields = ['result_value', 'result_file', 'is_retest']
        widgets = {
             # Auto-fill test ID
            'result_value': forms.TextInput(attrs={"class":'form-control', 'placeholder': 'Enter test result'}),
            'result_file': forms.ClearableFileInput(),
        }



class SystemExamForm(forms.ModelForm):
    class Meta:
        model = SystemExamination
        fields = ['heent', 'lungs', 'cardiovascular', 'gastrointestinal',
                  'genitourinary', 'musculoskeletal', 'neurological']
        
        widgets = {
            'heent': forms.Textarea(attrs={"class" : "form-control", 'rows': 2, 'placeholder': 'heent'}),
            'lungs': forms.Textarea(attrs={"class" : "form-control", 'rows': 2, 'placeholder': 'lungs'}),
            'cardiovascular': forms.Textarea(attrs={"class" : "form-control", 'rows': 2, 'placeholder': ''}), 
            'gastrointestinal': forms.Textarea(attrs={"class" : "form-control", 'rows': 2, 'placeholder': ''}),
            'genitourinary': forms.Textarea(attrs={"class" : "form-control", 'rows': 2, 'placeholder': ''}), 
            'musculoskeletal': forms.Textarea(attrs={"class" : "form-control", 'rows': 2, 'placeholder': ''}), 
            'neurological': forms.Textarea(attrs={"class" : "form-control", 'rows': 2, 'placeholder': ''}),
        }
        
    def clean_heent(self):
        heent = self.cleaned_data.get('heent')
        if not heent:
            raise forms.ValidationError('heent is required')
        return heent
    
    def clean_lungs(self):
        lungs = self.cleaned_data.get('lungs')
        if not lungs:
            raise forms.ValidationError('lungs is required')
        return lungs
    
    def clean_():
        pass
    def clean_():
        pass
    def clean_():
        pass
    def clean_():
        pass
    def clean_():
        pass

class TriageForm(forms.ModelForm):
    class Meta:
        model = TriageRecord
        fields = ['blood_pressure', 'pulse_rate', 'respiratory_rate',
                  'temperature', 'weight', 'height', 'oxygen_saturation']
    

    def clean_blood_pressure(self):
        blood_pressure = self.cleaned_data.get('blood_pressure')
        if not blood_pressure:
            raise forms.ValidationError("Blood pressure is required")
        pattern = r"^\d{2,3}/\d{2,3}$"
        if not re.match(pattern, blood_pressure):
            raise forms.ValidationError("Blood pressure should be written in the form 120/80")
        return blood_pressure
    
    def clean_pulse_rate(self):
        pulse_rate = self.cleaned_data.get('pulse_rate')
        if not pulse_rate:
            raise forms.ValidationError('Pulse rate is required')
        pattern = r"^(?:[3-9]\d|1\d{2}|2[0-1]\d|220)$"
        if not re.match(pattern, pulse_rate):
            raise forms.ValidationError("Invalid value")
        return pulse_rate
    
    def clean_respiratory_rate(self):
        respiratory_rate = self.cleaned_data.get('respiratory_rate')
        if not respiratory_rate:
            raise forms.ValidationError("Respiratory rate is required")
        pattern = r"^(?:[8-9]|[1-5]\d|60)$"
        if not re.match(pattern, respiratory_rate):
            raise forms.ValidationError("Invalid value")
        return respiratory_rate


    def clean_temperature(self):
        temperature = self.cleaned_data.get('temperature')
        if not temperature:
            raise forms.ValidationError("Temperature is required")
        elif temperature > 39 or temperature < 35:
            raise forms.ValidationError("Invalid value")
        return temperature


    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if not weight:
            raise forms.ValidationError("weight is required")
        elif weight < 0 or weight > 200:
            raise forms.ValidationError("Invalid value")
        return weight

    def clean_height(self):
        height = self.cleaned_data.get('height')
        if not height:
            raise forms.ValidationError("height is required")
        elif height < 0 and height > 300:
            raise forms.ValidationError("Invalid value")
        return height

    def clean_oxygen_saturation(self):
        oxygen_saturation = self.cleaned_data.get('oxygen_saturation')
        if not oxygen_saturation:
            raise forms.ValidationError("Oxygen Saturation is required")
        pattern_oxygen_saturation = r"\b(9[0-9](?:\.\d{1,2})?|100(\.0{1,2})?)%\b"
        if re.match(pattern_oxygen_saturation, oxygen_saturation):
            raise forms.ValidationError("Invalid value")
        return oxygen_saturation



class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = [
            'chief_complaint', 'history_of_present_illness', 'investigations', 'management_plan',
            'clinical_diagnosis', 'treatment_plan', 'advice', 'physical_examination',
        ]
        widgets = {
            'chief_complaint': forms.Textarea(attrs={"class" : "form-control", 'rows': 3, 'placeholder': 'chief complaint'}),
            'history_of_present_illness': forms.Textarea(attrs={"class" : "form-control", 'rows': 3, 'placeholder': ''}),
            'physical_examination': forms.Textarea(attrs={"class" : "form-control", 'rows': 3, 'placeholder': ''}),
            'investigations': forms.Textarea(attrs={"class" : "form-control", 'rows': 3, 'placeholder': ''}),
            'management_plan': forms.Textarea(attrs={"class" : "form-control", 'rows': 3, 'placeholder': ''}),
            'clinical_diagnosis': forms.Textarea(attrs={"class" : "form-control", 'rows': 3, 'placeholder': ''}),
            'treatment_plan': forms.Textarea(attrs={"class" : "form-control", 'rows': 3, 'placeholder': ''}),
            'advice': forms.Textarea(attrs={"class" : "form-control", 'rows': 3, 'placeholder': ''}),
        }

        
class AddAppointmentForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = ['next_appointment_date', 'physician_signature']

        widgets = {
            'next_appointment_date': forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
            'physician_signature': forms.Textarea(attrs={"class" : "form-control", 'rows': 5, 'placeholder': 'Remark'}),
        }
    
    def clean_next_appointment_date(self):
        if not self.cleaned_data.get('next_appointment_date'):
            raise forms.ValidationError('Date is required')
        # further validation
        return self.cleaned_data.get('next_appointment_date')

    def clean_physician_signature(self):
        if not self.cleaned_data.get('physician_signature'):
            raise forms.ValidationError('Remark is required')
        # further validation
        return self.cleaned_data.get('physician_signature')