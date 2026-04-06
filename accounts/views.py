from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Sum
from reportlab.pdfgen import canvas
from django.http import HttpResponse, JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import translation
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext as _
from .models import Notification, Staff
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm

# def login_view(request):
#     if request.method == 'POST':
#         login_form = CustomLoginForm(request.POST)
#         if login_form.is_valid():
#             user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
#             if user is not None:
#                  login(request, user)
#                  return redirect('dashboard')
#     else:
#         login_form = CustomLoginForm()
#     return render(request, 'login_page.html', {'form': login_form})

# @login_required
# def dashboard(request):
#     staff = request.user
     
#     if not staff.is_authenticated:
#         return redirect('login')
     
#     if staff.role == 'receptionist' and staff.department == 'registrar':
#         return redirect('receptionist_dashboard')
     
#     elif staff.role == 'nurse' and staff.department == 'registrar':
#         return redirect('triage')
     
#     elif staff.role == 'doctor':
#         return redirect('doctor_dashboard')
     
#     elif staff.role == 'cashier' and staff.department == 'finance':
#         return redirect('cashier_dashboard')
     
#     elif staff.role == 'lab_technician' and staff.department == 'lab':
#         return redirect('lab_dashboard')
     
#     elif staff.role == 'pharmacist' and staff.department == 'pharmacy':
#         return redirect('pharmacist_dashboard')
        
#     return redirect('login')


def login_view(request):
    """Handles user login."""
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {user.get_full_name()}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = CustomLoginForm()

    return render(request, 'login_page.html', {'form': form})


@login_required
def dashboard(request):
    """
    Redirects the logged-in user to their role-specific dashboard.
    """
    staff = request.user

    role_redirect_map = {
        
        ('receptionist', 'registrar'): 'receptionist_dashboard',
        ('nurse', 'registrar'): 'triage',
        ('doctor', None): 'doctor_dashboard',
        ('cashier', 'finance'): 'cashier_dashboard',
        ('lab_technician', 'lab'): 'lab_dashboard',
        ('pharmacist', 'pharmacy'): 'pharmacist_dashboard',
    }

    # Determine redirect based on role and department
    redirect_url = role_redirect_map.get((staff.role, staff.department))
    if not redirect_url and staff.role in ['doctor']:
        redirect_url = 'doctor_dashboard'

    if redirect_url:
        return redirect(redirect_url)

    # fallback to login if role/department not mapped
    messages.warning(request, "Your role/department is not configured for a dashboard.")
    return redirect('login')

@login_required
def change_language(request):
    pass

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    notified = notifications
    for notif in notified:
         notif.is_read = True
         notif.save()
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def notifications_count(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
    return JsonResponse({'count' : len(notifications)}, safe=False)


def notify_department_staff(department_name, message):
    """
    Sends a notification to all staff members in the specified department.
    
    :param department_name: Name of the department to filter staff
    :param message: The notification message to send
    :return: A dictionary with success and failed notifications
    """
    try:
        # Fetch staff members in the given department
        if department_name == 'all':
            staff_members = Staff.objects.all()
        else:
            staff_members = Staff.objects.filter(department=department_name)

        if not staff_members.exists():
            return {"status": "error", "message": f"No staff found in the department: {department_name}"}

        success_count = 0
        failed_count = 0

        for staff in staff_members:
            user = staff.user  # Assuming Staff model has a ForeignKey to User
            if user:  # Ensure the user has an email (or any notification method)
                try:
                    send_notification(user, message)  # Call your notification function
                    success_count += 1
                except Exception as e:
                    print(f"Failed to send notification to {user.email}: {e}")
                    failed_count += 1

        return {"status": "success", "notified": success_count, "failed": failed_count}

    except ObjectDoesNotExist:
        return {"status": "error", "message": "Department does not exist"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_notification(user, message):
    staff = Staff.objects.filter(username=user).first()
    notification = Notification.objects.create(recipient=staff, message=message)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{staff.id}",
        {
            "type": "send_notification",
            "message": message,
        },
    )

def notify_staff(user, message):
     try:
        if user:
            notification = Notification.objects.create(
                 recipient=user,
                 message=message,
            )
            notification.save()
     except Exception as e:
          print(str(e))


def notify_department_staffs(department_name, role, message):
    try:
        # Fetch staff members in the given department
        if department_name == 'all':
            staff_members = Staff.objects.all()
        elif department_name and role:
            staff_members = Staff.objects.filter(department=department_name, role=role)
        elif department_name and not role:
             staff_members = Staff.objects.filter(department_name=department_name)
        elif not department_name and role:
             staff_members = Staff.objects.filter(role=role)
        else:
            return
        for staff in staff_members:
            # Assuming Staff model has a ForeignKey to User
            notify_staff(staff, message)
    except Exception as e:
         print(str(e))


# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from .forms import CustomLoginForm

# def login_view(request):
#     """Handles user login."""
#     if request.method == 'POST':
#         form = CustomLoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']

#             user = authenticate(request, username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 messages.success(request, f"Welcome, {user.get_full_name}!")
#                 return redirect('dashboard')
#             else:
#                 messages.error(request, "Invalid username or password")
#     else:
#         form = CustomLoginForm()

#     return render(request, 'login_page.html', {'form': form})


# @login_required
# def dashboard(request):
#     """
#     Redirects the logged-in user to their role-specific dashboard.
#     """
#     staff = request.user

#     role_redirect_map = {
#         ('receptionist', 'registrar'): 'receptionist_dashboard',
#         ('nurse', 'registrar'): 'triage',
#         ('doctor', None): 'doctor_dashboard',
#         ('cashier', 'finance'): 'cashier_dashboard',
#         ('lab_technician', 'lab'): 'lab_dashboard',
#         ('pharmacist', 'pharmacy'): 'pharmacist_dashboard',
#     }

#     # Determine redirect based on role and department
#     redirect_url = role_redirect_map.get((staff.role, staff.department))
#     if not redirect_url and staff.role in ['doctor']:
#         redirect_url = 'doctor_dashboard'

#     if redirect_url:
#         return redirect(redirect_url)

#     # fallback to login if role/department not mapped
#     messages.warning(request, "Your role/department is not configured for a dashboard.")
#     return redirect('login')


# @login_required
# def logout_view(request):
    """Logs out the user and redirects to login page."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')