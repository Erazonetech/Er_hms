from registrar.models import Patient
from django.db import models
from django.conf import settings

class Visit(models.Model):
    URGENCY_CHOICES = [('urgent', 'Urgent'), ('non_urgent', 'Non-Urgent')]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visits')
    visit_date = models.DateTimeField(auto_now_add=True)
    chief_complaint = models.TextField(null=True, blank=True)  # C/C
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='non_urgent')
    history_of_present_illness = models.TextField(null=True, blank=True)  # HPI
    physical_examination = models.TextField(null=True, blank=True)  # P/E
    investigations = models.TextField(null=True, blank=True)  # Ix
    management_plan = models.TextField(null=True, blank=True)  # Mx
    clinical_diagnosis = models.TextField(null=True, blank=True)  # Clinical Dx
    treatment_plan = models.TextField(null=True, blank=True)  # Treatment Dx
    advice = models.TextField(null=True, blank=True)
    next_appointment_date = models.DateField(blank=True, null=True)
    attending_physician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'doctor'})
    physician_signature = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)  # Mark visit as active by default
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending_payment', 'Pending Payment'),
            ('triage', 'Triage'),
            ('ward_transfer', 'Transferred to Ward'),
            ('seen', 'Seen'),
            ('sent_to_lab', 'Sent to Lab'),
            ('sys_exam', 'System Examination'),
            ('prescribed', 'Prescribed'),
            ('completed', 'Completed'),
        ],
        default='pending_payment'
    )
    assigned_ward = models.CharField(
        max_length=20,
        choices=[
            ('ipd', 'In Patient Department'),
            ('opd', 'Out Patient Department'),
            ('er', 'Emergency')
        ],
        default='opd'
        )
    @classmethod
    def get_active_visit(cls, patient):
        """Get the active visit for a patient."""
        return cls.objects.filter(patient=patient, is_active=True).first()
    def __str__(self):
        return f"Visit on {self.visit_date} by {self.patient}"

class TriageRecord(models.Model):
    STATUS_CHOICE = (('pending', 'Pending'), ('completed', 'Completed'))

    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='triage_record')
    blood_pressure = models.CharField(max_length=20, blank=True)  # BP
    pulse_rate = models.CharField(max_length=15, blank=True, null=True)  # PR
    respiratory_rate = models.CharField(max_length=10, blank=True, null=True)  # RR
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)  # T0
    weight = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)  # Wt
    height = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)  # Ht
    bmi = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)  # BMI
    oxygen_saturation = models.CharField(max_length=4, blank=True, null=True)  # pO2
    status = models.CharField(max_length=20, choices=STATUS_CHOICE, default='pending')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'nurse'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vitals for {self.visit}"


class SystemExamination(models.Model):
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='system_examination')
    heent = models.TextField(blank=True)  # HEENT
    lungs = models.TextField(blank=True)  # LGS
    cardiovascular = models.TextField(blank=True)  # CVS
    gastrointestinal = models.TextField(blank=True)  # GIS
    genitourinary = models.TextField(blank=True)  # GUS
    musculoskeletal = models.TextField(blank=True)  # MSS
    neurological = models.TextField(blank=True)  # NS

    def __str__(self):
        return f"System Exam for {self.visit}"
    
class LabTestCategory(models.Model):
    TEST_TYPE = (
        ('hematology_test', 'Hematology Tests'),
        ('microbiology_test', 'Microbiology Tests'),
        ('clinical_chemistry_test', 'Clinical Chemistry Test'),
        ('urinalysis_and_body_fluid_test', 'Urinalysis & Body Fluids'),
        ('immunology_test', 'Immunology & Serology'),
        ('endocrinology_test', 'Endocrinology Test'),
        ('tumer_test', 'Tumor Markers'),
        ('covid_19', 'COVID-19 RT-PCR'),
    )
    """Broad classification of lab tests (e.g., Hematology, Microbiology, Biochemistry)."""
    name = models.CharField(max_length=100, choices=TEST_TYPE, unique=True)

    def __str__(self):
        return self.name


class LabTest(models.Model):
    """Represents an individual lab test (e.g., CBC, Blood Glucose, ESR)."""
    category = models.ForeignKey(LabTestCategory, on_delete=models.CASCADE, related_name="tests")
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class LabTestRequest(models.Model):
    """Tracks lab test orders linked to a patient visit."""
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    is_urgent = models.BooleanField(default=False)
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="lab_requests")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="lab_requests")
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    notes = models.TextField(blank=True, null=True)
    tests = models.ManyToManyField(LabTest, related_name="lab_test_requests")  # Many-to-many relationship with LabTest
    is_payed = models.BooleanField(default=False)

    def __str__(self):
        return f"Lab Request for {self.visit.patient.first_name} ({self.get_status_display()})"

    def total_price(self):
        return self.tests.aggregate(total=models.Sum('price'))['total'] or 0

    class Meta:
        ordering = ['-requested_at']


class LabTestResult(models.Model):
    """Stores the results of lab tests performed."""
    lab_request = models.ForeignKey(LabTestRequest, on_delete=models.CASCADE, related_name="results")
    result_value = models.CharField(max_length=255, blank=True, null=True)  # Store numeric/text results
    result_file = models.FileField(upload_to="lab_results/", blank=True, null=True)  # Optional file upload (PDF, image)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="lab_results")
    performed_at = models.DateTimeField(auto_now_add=True)
    is_retest = models.BooleanField(default=False)  # Flag if this result is from a retest

    def __str__(self):
        return f"{self.test.name} - {self.result_value or 'Pending'}"

class LabResult(models.Model):
    """Lab results for a test request, containing multiple test items."""
    lab_request = models.OneToOneField(LabTestRequest, on_delete=models.CASCADE, related_name="lab_result")
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_results")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    is_finalized = models.BooleanField(default=False)

    def __str__(self):
        return f"Lab Result for Request {self.lab_request.id}"


class LabResultItem(models.Model):
    """Stores test-specific results dynamically using a key-value structure."""
    lab_result = models.ForeignKey(LabResult, on_delete=models.CASCADE, related_name="result_items")
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name="result_items")
    result_data = models.JSONField(default=dict)  # Dynamic key-value storage

    def __str__(self):
        return f"Result for {self.test.name} (Request {self.lab_result.lab_request.id})"
class LabTestParameter(models.Model):
    """Defines expected result fields per test type."""
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE, related_name="parameters")
    name = models.CharField(max_length=100)  # e.g., "WBC", "Glucose Level"
    unit = models.CharField(max_length=50, blank=True, null=True)  # e.g., "g/dL", "mg/dL"
    reference_range = models.CharField(max_length=100, blank=True, null=True)  # e.g., "4.0 - 10.0 x10^9/L"

    def __str__(self):
        return f"{self.test.name} - {self.name}"


class Drug(models.Model):
    """Model for available drugs in the hospital pharmacy."""
    name = models.CharField(max_length=255, unique=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit (e.g., per tablet, per bottle)
    stock_quantity = models.PositiveIntegerField(default=0)  # To track availability

    def __str__(self):
        return self.name

class Prescription(models.Model):
    """Model for a prescription linked to a visit."""
    visit = models.ForeignKey('Visit', on_delete=models.CASCADE, related_name='prescriptions')
    prescribed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'doctor'})
    date_prescribed = models.DateTimeField(auto_now_add=True)
    is_dispensed = models.BooleanField(default=False)  # To track if prescription is fulfilled
    is_payed = models.BooleanField(default=False)

    def total_cost(self):
        """Calculate total cost of all prescribed drugs."""
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Prescription #{self.id} for {self.visit.patient}"

class PrescriptionItem(models.Model):
    """Model for individual drugs in a prescription."""
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)  # Example: "2 tablets twice a day"
    quantity = models.PositiveIntegerField()  # Total units prescribed
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    def total_price(self):
        """Calculate total price for this prescription item."""
        return self.quantity * self.price_per_unit

    def __str__(self):
        return f"{self.drug.name} ({self.dosage})"