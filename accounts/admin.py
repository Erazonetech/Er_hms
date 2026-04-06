from django.contrib import admin
from .models import  Staff, Notification
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm  # Import the custom form

admin.site.site_title = 'HMS Admin'
admin.site.site_header = 'HMS Admin'
admin.site.index_title = 'HMS Admin'

# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm  # Use custom form for adding users
    model = Staff
    list_display = ['username', 'email', 'role', 'department']
    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'middle_name', 'last_name' ,'email', 'password', 'role', 'department')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'first_name', 'middle_name',  'last_name' ,'email', 'password', 'role', 'department')}),
    )

admin.site.register(Staff, CustomUserAdmin)  # Register the user model in admin
@admin.register(Notification)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('recipient', 'is_read')
