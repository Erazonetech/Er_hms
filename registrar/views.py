from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.views import notify_department_staffs
from .models import Appointments, Patient, Zone, Woreda
from finance.models import Organization, Service, Payment
from .forms import AppointmentForm, PatientForm, AddressForm
from hospital_app.models import Visit, TriageRecord
from django.contrib import messages
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta

@login_required
def receptionist_dashboard(request):
    try:
        search_query = request.GET.get('search', '')
        org_filter = request.GET.get('organization', '')

        today = now().date()
        appointments = Appointments.objects.filter(date=today)

        patients = Patient.objects.all()
        if search_query:
            patients = patients.filter(
                first_name__icontains=search_query
            ) | patients.filter(last_name__icontains=search_query) | patients.filter(middle_name__icontains=search_query) | patients.filter(phone__icontains=search_query)

        if org_filter:
            patients = patients.filter(organization__id=org_filter)

        organizations = Organization.objects.all()
        
        patients = patients.order_by('-record_no')[:5]

        return render(request, 'receptionist.html', {
            'patients': patients,
            'organizations': organizations,
            'search_query': search_query,
            'appointments': appointments,
            'selected_org': org_filter
        })
    except Exception as e:
        print(str(e))

@login_required
def list_appointment(request):
    today = now().date()
    appointments = Appointments.objects.filter(date=today)
    upcomin_appointments = Appointments.objects.filter(date=(today - timedelta(days=1)))
    if request.user.role == 'doctor':
        appointments = appointments.filter(appointed_by=request.user)
        upcomin_appointments = upcomin_appointments.filter(appointed_by=request.user)
    return render(
        request, 
        'appointment_list.html',
        {
            'appointments': appointments,
            'upcomin_appointments': upcomin_appointments
        }
    )

@login_required
def add_appointment(request, pk):
    if not request.user.role == 'doctor':
        messages.error(request, 'You are not allowed to add appointment.')
        return redirect('dashboard')
    today = now().date()
    patient = get_object_or_404(Patient, pk=pk)
    appointment, _ = Appointments.objects.get_or_create(date=today, patient=patient, appointed_by=request.user, )
    form = AppointmentForm(instance=appointment)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Visit details Updated.")
            if request.user.role == 'doctor':
                visit = Visit.objects.filter(
                    is_active = True,
                    attending_physician=request.user,
                    patient=patient,
                ).first()
                if not visit:
                    return redirect('doctor_dashboard')    
                return redirect('doctor_detail', patient_id=patient.id, visit_id=visit.id)
            return redirect('view_patient', pk=patient.id)
    return render(request, 'add_appointment.html', {'form': form})




@login_required
def add_patient(request):
    if request.method == 'POST':
        patient_form = PatientForm(request.POST)
        address_form = AddressForm(request.POST)
        
        if patient_form.is_valid() and address_form.is_valid():
            address = address_form.save()
            patient = patient_form.save(commit=False)
            patient.address = address
            patient.save()
            # Step 2: Create Payment for Registration
            messages.success(request, "Patient registered successfully, pending for checkin!")
            return redirect('view_patient', pk=patient.id)

    else:
        # make the adress_form fields zone and woreda to have none objects in the 
        
        patient_form = PatientForm()
        address_form = AddressForm()

    return render(request, 'patient_form.html', {
        'patient_form': patient_form,
        'address_form': address_form
    })



@login_required
def edit_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    address = patient.address

    if request.method == 'POST':
        patient_form = PatientForm(request.POST, instance=patient)
        address_form = AddressForm(request.POST, instance=address)

        if patient_form.is_valid() and address_form.is_valid():
            address_form.save()
            patient_form.save()
            messages.success(request, "Patient updated successfully!")
            return redirect('view_patient', pk=patient.id)

    else:
        patient_form = PatientForm(instance=patient)
        address_form = AddressForm(instance=address)

    return render(request, 'patient_form.html', {
        'patient_form': patient_form,
        'address_form': address_form,
        'patient': patient
    })

@login_required
def view_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    triage_info = TriageRecord.objects.filter(visit__patient=patient).order_by('-created_at').first()
    appointments = Appointments.objects.filter(patient=patient)
    appointments = appointments.exclude(is_seen=True)
    return render(request, 'patient_detail.html', {'patient': patient, 'appointments': appointments, 'triage_info': triage_info})


@login_required
def view_appointments(request):
    today = now().date()
    appointments = Appointments.objects.filter(date=today)
    return render(
        request, 
        'patient_detail.html', 
        {'appointments': appointments}
    )


@login_required
def add_visit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    
    # Step 1: Create Visit object
    visit = Visit.objects.create(patient=patient)
    
    # Step 2: Create Payment for doctor visit if he is not new patient.
    visit_service, _ = Service.objects.get_or_create(name="Card", defaults={"price": 50})
    Payment.objects.create(visitor=visit, service=visit_service, amount=visit_service.price, status="PENDING")
    notify_department_staffs('finance', 'cashier', f'Patient { visit.patient.name } is ready for payment')
    messages.success(request, f"Patient {patient.first_name} added to visit. Payment pending.")
    return redirect('receptionist_dashboard')

@login_required
def get_zones(request):
    region = request.GET.get('region')
    zones = Zone.objects.filter(region=region).all()
    return JsonResponse(list(zones.values('id', 'name')), safe=False)

# AJAX view to fetch woredas based on selected zone
@login_required
def get_woredas(request):
    zone_id = request.GET.get('zone_id')
    woredas = Woreda.objects.filter(zone_id=zone_id).all()
    return JsonResponse(list(woredas.values('id', 'name')), safe=False)