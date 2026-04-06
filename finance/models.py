from django.db import models
from hospital_app.models import Visit

# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Service(models.Model):
    SERVICE_TYPES = [
        ('registration', 'Registration'),
        ('visit', 'Doctor Visit'),
        ('lab_test', 'Lab Test'),
        ('prescription', 'Prescription'),
    ]

    name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('credit', 'Credit'),
    ]

    visitor = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='payments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    organization_letter = models.FileField(upload_to='letters/', null=True, blank=True)
    signed_attachment = models.FileField(upload_to='attachments/', null=True, blank=True)

    def __str__(self):
        return f"{self.visitor.patient} - {self.service.name} - {self.status}"
