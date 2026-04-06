from django.urls import path
from . import views

urlpatterns = [
    # Prescription URLs
   path('triage/', views.triage_dashboard, name='triage'),
   path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
   path('doctor_detail/<int:patient_id>/<int:visit_id>', views.doctor_detail, name='doctor_detail'),
   path('add_lab_request/<int:visit_id>', views.add_lab_test_request, name='add_lab_request'),
   path('edit_lab_request/<int:pk>', views.edit_lab_test_request, name='edit_lab_request'),
   path('update_visit/<int:visit_id>', views.update_visit_by_doctor, name='update_visit'),
   path('fill_triage/<int:triage_id>', views.fill_triage, name='fill_triage'),
   path('add_system_exam/<int:visit_id>', views.add_system_exam, name='add_system_exam'),
   path('assign_to_ward/<int:visit_id>', views.assign_to_ward, name='assign_to_ward'),
   path('get_doctor_by_department/', views.get_doctor_by_department, name='get_doctor_by_department'),
   path('lab_technician/', views.pending_lab_requests, name='lab_dashboard'),
   path('submit_lab_result/<int:test_id>', views.submit_lab_results, name='submit_lab_result'),
   path('review_lab_results/<int:visit_id>', views.review_lab_results, name='review_lab_results'),
   path('prescribe_view/<int:visit_id>', views.prescribe_view, name='prescribe_view'),
   path('pharmacist/', views.prescription_queue_list, name='pharmacist_dashboard'),
   path('dispense/<int:prescription_id>', views.dispense_view, name='dispense_view'),
   path('prescription_detail_view/<int:prescription_id>', views.prescription_detail_view, name='prescription_detail'),
]

