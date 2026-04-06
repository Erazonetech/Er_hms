from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from accounts.models import Staff, Notification
from accounts.views import notify_department_staffs, notify_staff
from hospital_app.models import LabResult, LabResultItem, LabTestRequest, SystemExamination, TriageRecord, Visit, Prescription, PrescriptionItem, Drug
from .helper import calculate_bmi
from .forms import AddAppointmentForm, SystemExamForm, TriageForm, VisitForm, LabTestRequestForm
from django.contrib import messages
from registrar.models import Patient
from django.utils.timezone import now
from datetime import timedelta
from finance.models import Service, Payment

yesterday = now().date() - timedelta(days=1)

@login_required
def doctor_dashboard(request):
    # add vital sign data suggesions
    today = now().date()
    lab_request = LabTestRequest.objects.filter(
        requested_by=request.user,
    )
    lab_request = lab_request.exclude(status='completed')
    appointments = Visit.objects.filter(
        is_active = False, 
        next_appointment_date=today, 
        assigned_ward=request.user.department
    )
    visits = Visit.objects.filter(
        is_active = True, 
        assigned_ward=request.user.department,
    ).order_by('-visit_date')
    visits = visits.exclude(status='completed')

    visits = visits.exclude(attending_physician=request.user)
    my_visits = Visit.objects.filter(
        is_active = True,
        attending_physician=request.user
    ).order_by('-visit_date')
    my_visits = my_visits.exclude(status='completed')
    return render(request, 'doctor_dashboard.html', {
        'my_visits': my_visits, 
        'visits': visits, 
        'appointments': appointments,
        'lab_requests': lab_request,
    })


@login_required
def doctor_detail(request, patient_id, visit_id):
    #filter with date to confirm accuracy
    patient = get_object_or_404(Patient, id=patient_id)
    visit = get_object_or_404(Visit, id=visit_id)
    visit.status = 'seen'
    visit.save()
    
    visits = Visit.objects.filter(patient=patient, is_active=False).order_by("-visit_date")
    
    lab_results = LabResult.objects.filter(lab_request__visit=visit).order_by("-reviewed_at")
    lab_requests = LabTestRequest.objects.get(visit=visit)
    
    vitals = TriageRecord.objects.filter(visit=visit).order_by("-created_at").first()
    form = VisitForm(instance=visit)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Diagnosis details Updated.")
        
    return render(request, "doctor_detail_view.html", {
        "patient": patient,
        "visits": visits,
        'visit_id': visit.id,
        "lab_results": lab_results,
        'lab_requests': lab_requests,
        "triage_info": vitals,
        'form': form
    })

@login_required
def update_visit_by_doctor(request, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)
    form = VisitForm(instance=visit)
    if request.method == 'POST':
        form = VisitForm(request.POST, instance=visit)
        if form.is_valid():
            form.save()
            messages.success(request, "Visit details Updated.")
            return redirect('doctor_detail', patient_id=visit.patient.id, visit_id=visit_id)
    return render(request, 'visit_form.html', {'form': form})

@login_required
def new_appointment(request, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)
    form = AddAppointmentForm(instance=visit)
    if request.method == 'POST':
        form = AddAppointmentForm(request.POST, instance=visit)
        if form.is_valid():
            form.save()
            messages.success(request, "Visit details Updated.")
            return redirect('doctor_detail', patient_id=visit.patient.id, visit_id=visit_id)
    return render(request, 'add_appointment.html', {'form': form})

@login_required
def add_system_exam(request, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)
    system_exam = get_object_or_404(SystemExamination, visit__id=visit_id)
    
    if request.method == 'POST':
        form = SystemExamForm(request.POST, instance=system_exam)
        if form.is_valid():
            form.save()
            messages.success(request, "System Exam details Updated.")
            return redirect('doctor_detail', patient_id=visit.patient.pk, visit_id=visit.pk)
    else:
        form = SystemExamForm(instance=system_exam)
    return render(request, 'system_exam_form.html', {'form': form})

@login_required
def triage_dashboard(request):
    queued_patients = TriageRecord.objects.filter(visit__status='triage', status='pending')
    patients_to_ward = TriageRecord.objects.filter(visit__status='triage', status='completed')
    return render(request, 'triage_dashboard.html', {"queued_patients": queued_patients, 'patients_to_ward': patients_to_ward})

@login_required
def fill_triage(request, triage_id):
    triage = get_object_or_404(TriageRecord, pk=triage_id)
    visit = Visit.objects.filter(id=triage.visit.id).first()

    form = TriageForm(instance=triage)

    if request.method == "POST":
        form = TriageForm(request.POST, instance=triage)
        visit = get_object_or_404(Visit, pk=triage.visit.id)

        if form.is_valid():
            # Get height and weight from the form data
            height = form.cleaned_data.get('height')
            weight = form.cleaned_data.get('weight')

            # Calculate BMI
            bmi = calculate_bmi(weight, height)

            # Save the calculated BMI into the triage instance
            triage.bmi = bmi
            triage.status = 'completed'

            # Save the triage form with updated BMI
            form.save()
        
            # Success message
            messages.success(request, "Triage details submitted.")
            if request.user.role == 'doctor':
                return redirect('doctor_detail', patient_id=visit.patient.pk, visit_id=visit.pk)
            return redirect('assign_to_ward', visit_id=visit.pk)  # Redirect after success

    return render(request, 'fill_triage.html', {"form": form, 'visit': visit})

@login_required
def assign_to_ward(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    if request.method == 'POST':
        visit.assigned_ward = request.POST.get('ward')
        visit.urgency = request.POST.get('urgency')
        visit.status = 'ward_transfer'
        attending_physician = get_object_or_404(Staff, id=request.POST.get('physician'))
        visit.attending_physician = attending_physician
        visit.save()
        if request.user.role == 'doctor':
            messages.success(request, "Patient info updated.")
            return redirect('doctor_detail', patient_id=visit.patient.pk, visit_id=visit.pk)
        notify_staff(attending_physician, f'Patient { visit.patient.name } is waiting for visit!')
        messages.success(request, f"Patient is now ready for doctor {attending_physician.get_ful_name}.")
        return redirect('triage')

    return render(request, 'assign_to_ward.html', {"visit": visit})




@login_required
def add_lab_test_request(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    if request.method == "POST":
        form = LabTestRequestForm(request.POST or None)
        if form.is_valid():
            lab_test_request = form.save(commit=False)
            lab_test_request.visit = visit  # Assign the visit to the lab test request
            lab_test_request.requested_by = request.user
            lab_test_request.save()  # Save the lab test request instance

            # Associate selected tests with the lab test request
            lab_test_request.tests.set(form.cleaned_data['tests'])
            # add payment for the tests needed
            lab_service, _ = Service.objects.get_or_create(name="Lab Test", defaults={"price": lab_test_request.total_price})
            Payment.objects.create(visitor=visit, service=lab_service, amount=lab_service.price, status="PENDING")
            messages.success(request, "Lab tests have been requested successfully!")
            notify_department_staffs('finance', 'cashier', f"patinet {visit.patient.name} is ready for payment for the Lab Test")
            return redirect('doctor_detail', patient_id=visit.patient.pk, visit_id=visit.pk)  # Redirect to a success page or another view
        else:
            
            # Optionally, show the errors in the form by adding them to the response context
            return render(request, 'add_lab_request.html', {'form': form, 'visit': visit})
    else:
        form = LabTestRequestForm(initial={'visit': visit})
    return render(request, 'add_lab_request.html', {'form': form, 'visit': visit})

@login_required
def edit_lab_test_request(request, pk):
    test = get_object_or_404(LabTestRequest, pk=pk)
    if request.method == 'POST':
        form = LabTestRequestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            return redirect('doctor_detail', patient_id=test.visit.patient.pk, visit_id=test.visit.pk) 
    else:
        form = LabTestRequestForm(instance=test)
    
    return render(request, 'add_lab_request.html', {'form': form})

@login_required
def submit_lab_results(request, test_id):
    lab_request = get_object_or_404(LabTestRequest, id=test_id)
    
    # Ensure a result entry exists
    lab_result, created = LabResult.objects.get_or_create(lab_request=lab_request)

    if request.method == "POST":
        # Process each test result dynamically
        for test in lab_request.tests.all():
            parameters = test.parameters.all()  # Get expected result fields
            
            # Store result data
            result_data = {}
            for param in parameters:
                value = request.POST.get(f"test_{test.id}_param_{param.id}")
                if value:
                    result_data[param.name] = value  # Store as key-value

            # Save results dynamically
            LabResultItem.objects.update_or_create(
                lab_result=lab_result,
                test=test,
                defaults={"result_data": result_data}
            )

        # Finalize result
        lab_result.reviewed_by = request.user
        lab_result.reviewed_at = now()
        lab_result.is_finalized = True
        lab_result.save()

        lab_request.status = "completed"
        lab_request.save()

        messages.success(request, "Lab results submitted successfully.")
        notify_staff(lab_request.visit.attending_physician, f'Patient { lab_request.visit.patient.name }\'s lab result is ready')
        return redirect("lab_dashboard")

    return render(request, "submit_lab_result.html", {"lab_request": lab_request})



@login_required
def pending_lab_requests(request):
    """Display all pending lab test requests for the lab technician."""
    pending_tests = LabTestRequest.objects.filter(status="requested").select_related('visit__patient')

    return render(request, "pending_lab_requests.html", {"pending_tests": pending_tests})

@login_required
def review_lab_results(request, visit_id):
    visit = get_object_or_404(Visit, id=visit_id)
    
    # Fetch the latest lab test request for this visit
    lab_request = LabTestRequest.objects.filter(visit=visit).order_by('-requested_at').first()
    
    # Get all associated test results
    lab_results = LabResult.objects.filter(lab_request=lab_request).first()
    
    # Result item
    result_item = LabResultItem.objects.filter(lab_result=lab_results)
    processed_results = []
    for result in result_item:
        try:
            test_data = result.result_data  # Assuming this is a JSON field
            processed_results.append({
                "test_name": result.test.name,
                "parameters": test_data,  # This is a list of dicts [{"name": "Hemoglobin", "value": "13.5", "unit": "g/dL", "normal_range": "12-16"}]
            })
        except Exception as e:
            print(f"Error parsing results for {result.test.name}: {e}")

    context = {
        "visit": visit,
        "lab_request": lab_request,
        "processed_results": processed_results,
    }
    return render(request, "review_lab_results.html", context)


@login_required
def prescribe_view(request, visit_id):
    visit = get_object_or_404(Visit, pk=visit_id)

    if request.method == "POST":
        drugs_selected = request.POST.getlist("drugs")  # List of selected drugs
        quantities = request.POST.getlist("quantities")  # Corresponding quantities
        dosages = request.POST.getlist("dosages")  # Corresponding dosages

        if not drugs_selected:
            messages.error(request, "Please select at least one drug to prescribe.")
            return redirect('prescribe_view', visit_id=visit_id)

        with transaction.atomic():  # Ensure everything is saved together
            prescription, created = Prescription.objects.get_or_create(
                visit=visit,
                prescribed_by=request.user
            )

            for i, drug_id in enumerate(drugs_selected):
                try:
                    drug = Drug.objects.get(id=drug_id)
                    quantity = int(quantities[i])
                    dosage = dosages[i]

                    PrescriptionItem.objects.create(
                        prescription=prescription,
                        drug=drug,
                        quantity=quantity,
                        price_per_unit=drug.price_per_unit,
                        dosage=dosage
                    )
                except (Drug.DoesNotExist, ValueError, IndexError):
                    messages.error(request, "Invalid data provided for prescription.")
                    return redirect('prescribe_view', visit_id=visit_id)
                
            prescription_service, _ = Service.objects.get_or_create(name="Prescription", defaults={"price": prescription.total_cost})
            Payment.objects.create(visitor=visit, service=prescription_service, amount=prescription_service.price, status="PENDING")
            notify_department_staffs('finance', 'cashier', f"patinet {visit.patient.name} is ready for payment for the Medications")
            messages.success(request, "Prescription ordered successfully, Payment is now ready.")
            return redirect('doctor_detail', patient_id=visit.patient.pk, visit_id=visit.pk)

    drugs = Drug.objects.all()
    return render(request, 'prescribe_form.html', {'visit': visit, 'drugs': drugs})

@login_required
def prescription_queue_list(request):
    prescriptions = Prescription.objects.filter(is_dispensed=False).order_by('-date_prescribed')
    return render(request, 'prescription_queue.html', {'prescriptions': prescriptions})



@login_required
def dispense_view(request, prescription_id):
    prescription = get_object_or_404(Prescription, pk=prescription_id)
    if request.method == "POST":
        with transaction.atomic():
            for item in prescription.items.all():
                if item.drug.stock_quantity < item.quantity:
                    messages.error(request, f"Not enough stock for {item.drug.name}.")
                    return redirect('prescription_queue_list')

                item.drug.stock_quantity -= item.quantity
                item.drug.save()

            prescription.is_dispensed = True
            prescription.save()
            messages.success(request, "Prescription dispensed successfully.")
            visit = get_object_or_404(Visit, pk=prescription.visit.id)
            visit.status = 'completed'
            visit.is_active = False
            visit.save()
            return redirect('prescription_queue_list')

    return render(request, 'dispense_confirm.html', {'prescription': prescription})


@login_required
def prescription_detail_view(request, prescription_id):
    """Displays detailed prescription information for dispensing."""
    prescription = get_object_or_404(Prescription, id=prescription_id)
    items = PrescriptionItem.objects.filter(prescription=prescription)

    # Calculate total cost
    total_price = prescription.total_cost()

    if request.method == "POST":
        prescription.status = "dispensed"
        prescription.is_dispensed = True
        prescription.save()
        messages.success(request, "Prescription has been dispensed successfully!")
        return redirect('pharmacist_dashboard')

    return render(request, 'prescription_detail.html', {
        'prescription': prescription,
        'items': items,
        'total_price': total_price
    })

@login_required
def get_doctor_by_department(request):
    department = request.GET.get('department')
    attending_physician = Staff.objects.filter(department=department, role='doctor').all()
    return JsonResponse(list(attending_physician.values('id', 'first_name', 'middle_name')), safe=False)
