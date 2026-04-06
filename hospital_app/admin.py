from django.contrib import admin
from .models import TriageRecord, Visit, LabTestCategory, LabTest, LabTestRequest, LabTestParameter, LabResult, LabResultItem, Drug, SystemExamination


admin.site.register(SystemExamination)
admin.site.register(Drug)
admin.site.register(LabTestParameter)
admin.site.register(LabTestCategory)
admin.site.register(LabTest)
admin.site.register(LabTestRequest)
admin.site.register(LabResult)
admin.site.register(LabResultItem)

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('id','patient', 'status')
    list_filter = ('visit_date', 'status')
    search_fields = ('status', 'patient__last_name')

@admin.register(TriageRecord)
class TriageAdmin(admin.ModelAdmin):
    list_display = ('status', 'visit', 'recorded_by')
    list_filter = ('status', 'created_at')
    search_fields = ('status', 'visit__patient__first_name', 'visit__patient__last_name')
