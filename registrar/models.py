from django.db import models
from datetime import date, timedelta

from hospital_management import settings

def get_dob_from_age(age: int) -> date:
    """Returns the date of birth given the age."""
    today = date.today()
    dob = today.replace(year=today.year - age)
    return dob


ethiopia_regions = [
    ("addis ababa", "Addis Ababa"),
    ("afar", "Afar"),
    ("amhara", "Amhara"),
    ("benishangul", "Benishangul-Gumuz"),
    ("dire dawa", "Dire Dawa"),
    ("gambela", "Gambela"),
    ('harari', "Harari"),
    ("oromia", "Oromia"),
    ("sidama", "Sidama"),
    ("south ethiopia", "South Ethiopia"),
    ("south west ethiopia", "South West Ethiopia"),
    ("central ethiopia", "Central Ethiopia"),
    ("somali", "Somali"),
    ("tigray", "Tigray")
]


class Zone(models.Model):
    region = models.CharField(max_length=100, choices=ethiopia_regions, default='south ethiopia')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Woreda(models.Model):
    zone = models.ForeignKey(Zone, related_name='woredas', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Address(models.Model):
    region = models.CharField(max_length=100, choices=ethiopia_regions, default='south ethiopia')
    zone = models.ForeignKey(Zone, related_name='addresses', on_delete=models.CASCADE)
    woreda = models.ForeignKey(Woreda, related_name='addresses', on_delete=models.CASCADE)
    kebele = models.CharField(max_length=100, null=True, blank=True)
    ketena = models.CharField(max_length=100, null=True, blank=True)
    house_no = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.region}, {self.zone}, {self.woreda}"

class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    record_no = models.CharField(max_length=8, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()  # Date of Birth
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    phone = models.CharField(max_length=15)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def name(self):
        return f"{self.first_name} {self.middle_name}  {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.middle_name} (MRN: {self.record_no})"
    
    def save(self, *args, **kwargs):
        if not self.dob and self.age:
            self.dob = get_dob_from_age(self.age)
        if not self.record_no:
            self.record_no = self.generate_unique_record_no()
        super().save(*args, **kwargs)

    @classmethod
    def generate_unique_record_no(cls):
        """Generate the next available 8-digit record_no (00000000 - 99999999)"""
        last_patient = cls.objects.order_by('-record_no').first()
        if last_patient and last_patient.record_no.isdigit():
            next_number = int(last_patient.record_no) + 1
        else:
            next_number = 0  # Start from 00000000

        return f"{next_number:08d}"

class Appointments(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    appointed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patient.name} on {self.date}"