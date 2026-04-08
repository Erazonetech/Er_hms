from . import views
from django.urls import path


urlpatterns = [
    # Prescription URLs
    path('notifications/', views.notifications, name='notifications'),
    path('notifications_count/', views.notifications_count, name='notifications_count'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('change_language/', views.change_language, name='change_language'),
    path('set_language/', views.change_language, name='set_language'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('dashboard/', views.dashboard_view, name='dashboard'),
]

