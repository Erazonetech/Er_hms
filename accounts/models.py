from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.models import AbstractUser

class Staff(AbstractUser):
    phone_number = models.CharField(max_length=15)
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
        ('lab_technician', 'Lab Technician'),
        ('pharmacist', 'Pharmacist'),
        ('admin', 'Administrator'),
        ('finance', 'Finance'),
        ('cashier', 'Cashier'),
    ]
    DEPARTMENT_CHOICES = [
        ('registrar', 'Registrar'),
        ('er', 'Emergency Room'),
        ('opd', 'Outpatient Department'),
        ('ipd', 'Inpatient Department'),
        ('mch', 'Mother and Child Department'),
        ('lab', 'Laboratory'),
        ('pharmacy', 'Pharmacy'),
        ('admin', 'Administration'),
        ('finance', 'Finance'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    middle_name = models.CharField(max_length=20)
    # groups = models.ManyToManyField(Group, related_name='staff_groups', blank=True)
    # user_permissions = models.ManyToManyField(Permission, related_name='staff_permissions', blank=True)

    @property
    def get_ful_name(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'
    
    def __str__(self):
    	return f"{self.username} - {self.role} ({self.department})"


class Notification(models.Model):
    recipient = models.ForeignKey(Staff, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.recipient.username}"
  