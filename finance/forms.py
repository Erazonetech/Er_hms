from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['service', 'amount', 'status', 'organization_letter', 'signed_attachment']
