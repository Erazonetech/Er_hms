from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('login')),
    path('admin/', admin.site.urls),
    path('clinic/', include('hospital_app.urls')),
    path('', include('accounts.urls')),
    path('finance/', include('finance.urls')),
    path('registrar/', include('registrar.urls')),
]

