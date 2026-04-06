from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
# urls.py
from django.urls import path


urlpatterns = [
    # Prescription URLs
    path('receptionist/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('patient/add/', views.add_patient, name='add_patient'),
    path('patient/edit/<int:pk>/', views.edit_patient, name='edit_patient'),
    path('patient/view/<int:pk>/', views.view_patient, name='view_patient'),
    path('patient/visit/<int:pk>/', views.add_visit, name='add_visit'),
    path('list_appointment/', views.list_appointment, name='list_appointment'),
    path('new_appointment/<int:pk>', views.add_appointment, name='new_appointment'),
    path('get-zones/', views.get_zones, name='get_zones'),
    path('get-woredas/', views.get_woredas, name='get_woredas'),
]