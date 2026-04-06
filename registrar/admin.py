from django.contrib import admin
from .models import  Patient, Address, Zone, Woreda, Address, Appointments


admin.site.register(Appointments)
admin.site.register(Zone)
admin.site.register(Woreda)


# Register your models here.
@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'middle_name', 'last_name')
    list_filter = ('created_at', 'gender')
    search_fields = ('first_name', 'last_name')


@admin.register(Address)
class PatientAddressAdmin(admin.ModelAdmin):
    list_display = ('region', 'zone', 'woreda')
    list_filter = ('region', 'zone', 'woreda', 'kebele')
    search_fields = ('region', 'zone')