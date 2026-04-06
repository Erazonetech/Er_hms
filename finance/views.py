from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Payment
from hospital_app.models import TriageRecord, Visit, LabTestRequest, Prescription
from django.contrib import messages
from accounts.views import notify_department_staffs


@login_required
def cashier_dashboard(request):
    pending_payments = Payment.objects.filter(status="PENDING")
    return render(request, 'cashier_dashboard.html', {"pending_payments": pending_payments})

@login_required
def process_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    service = payment.service.name
    # process the request based on the service type.
    if request.method == "POST":
        if service in ['Registration', 'Card', 'Doctor Visit']:
            payment.status = "COMPLETED"
            payment.save()

            #make the visit object to triage
            visit, _ = Visit.objects.get_or_create(id=payment.visitor.id)
            visit.status = 'triage'
            visit.save()
            # Create Triage Queue Entry
            TriageRecord.objects.create(visit=payment.visitor, status="pending")
            # find the triage nurse and send notification
            notify_department_staffs('registrar', 'nurse', f"Patient { payment.visitor.patient.name } is waiting for triage.")        
            messages.success(request, f"Payment for {payment.service.name} completed. Patient sent to triage.")
            return redirect('cashier_dashboard')

        elif service == 'Lab Test':
            payment.status = "COMPLETED"
            payment.save()

            # make the lab test request to paid
            lab_test = LabTestRequest.objects.filter(visit=payment.visitor.id).first()
            lab_test.is_payed = True
            lab_test.status = 'processing'
            lab_test.save()
            visit = get_object_or_404(Visit, pk=payment.visitor.id)
            visit.status = 'sent_to_lab'
            visit.save()
            # find the lab technician and send notification
            notify_department_staffs('lab', 'lab_technician', f"Patient {payment.visitor.patient} is waiting for test.")        
            messages.success(request, f"Payment for {payment.service.name} completed. Patient sent to Lab.")
            return redirect('cashier_dashboard')

        elif service == 'Prescription':
            payment.status = "COMPLETED"
            payment.save()

            # make the prescription request to paid
            prescription_item = Prescription.objects.filter(visit=payment.visitor.id).first()
            prescription_item.is_payed = True
            prescription_item.save()
            # Create Triage Queue Entry
            # find the triage nurse and send notification
            visit = get_object_or_404(Visit, pk=payment.visitor.id)
            visit.status = 'prescribed'
            visit.save()
            notify_department_staffs('pharmacy', 'pharmacist', f"Patient {payment.visitor.patient} with prescription is waiting for medication.")        
            messages.success(request, f"Payment for {payment.service.name} completed. Patient sent to Pharmacy.")
            return redirect('cashier_dashboard')
        else:
            messages.success(request, f"Payment for {payment.service.name} not completed. please try again.")
            return redirect('cashier_dashboard')
