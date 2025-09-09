from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import teacher, MissingStudentAlert, StudentStatusOverride
from driver.models import Busdriver

# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            teacher_obj = teacher.objects.get(email=email, password=password)
            request.session['teacher_id'] = teacher_obj.id
            request.session['teacher_name'] = teacher_obj.teacher_name
            return redirect('teacher:dashboard')
        except teacher.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return redirect('teacher:login')
    return render(request, 'teacher_login.html')

def dashboard(request):
    if 'teacher_id' not in request.session:
        return redirect('teacher:login')

    # Get active missing student alerts
    alerts = MissingStudentAlert.objects.filter(status='active').order_by('-reported_at')[:10]

    context = {
        'alerts': alerts,
        'teacher_name': request.session.get('teacher_name', '')
    }
    return render(request, 'teacher_dashboard.html', context)

def bus_tracking(request):
    if 'teacher_id' in request.session:
        teacher_id = request.session['teacher_id']
        teacher_obj = teacher.objects.get(id=teacher_id)
        # For simplicity, show all active buses and their drivers
        drivers = Busdriver.objects.all()
        return render(request, 'bus_tracking.html', {
            'teacher': teacher_obj,
            'drivers': drivers
        })
    else:
        return redirect('teacher:login')

def logout(request):
    request.session.flush()
    return redirect('teacher:login')

def manual_override(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        bus_route = request.POST.get('bus_route')
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')

        teacher_id = request.session['teacher_id']
        teacher_obj = teacher.objects.get(id=teacher_id)

        # Create the override record
        override = StudentStatusOverride.objects.create(
            student_name=student_name,
            bus_route=bus_route,
            action=action,
            applied_by=teacher_obj,
            notes=notes
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Manual override applied: {student_name} marked as {action}',
            'override_id': override.id
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def report_missing_student(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        bus_route = request.POST.get('bus_route')
        details = request.POST.get('details')

        teacher_id = request.session['teacher_id']
        teacher_obj = teacher.objects.get(id=teacher_id)

        # Create an alert for immediate action
        alert = MissingStudentAlert.objects.create(
            student_name=student_name,
            bus_route=bus_route,
            last_seen=details,
            parent_contact='Contact school administration',
            reported_by=teacher_obj
        )

        return JsonResponse({
            'status': 'success',
            'message': f'Missing student alert created for {student_name}',
            'alert_id': alert.id
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def resolve_alert(request, alert_id):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    try:
        alert = MissingStudentAlert.objects.get(id=alert_id)
        alert.status = 'resolved'
        alert.save()

        return JsonResponse({
            'status': 'success',
            'message': f'Alert for {alert.student_name} has been resolved'
        })
    except MissingStudentAlert.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Alert not found'})

def get_alerts(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    alerts = MissingStudentAlert.objects.filter(status='active').order_by('-reported_at')[:20]
    alerts_data = []

    for alert in alerts:
        alerts_data.append({
            'id': alert.id,
            'student_name': alert.student_name,
            'bus_route': alert.bus_route,
            'last_seen': alert.last_seen,
            'parent_contact': alert.parent_contact,
            'reported_at': alert.reported_at.strftime('%Y-%m-%d %H:%M:%S')
        })

    return JsonResponse({
        'status': 'success',
        'alerts': alerts_data
    })

def get_all_bus_locations(request):
    if 'teacher_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Not authenticated'})

    drivers = Busdriver.objects.all()
    buses_data = []

    for driver in drivers:
        if driver.latitude and driver.longitude:
            buses_data.append({
                'driver_id': driver.id,
                'driver_name': driver.bus_driver,
                'bus_no': driver.bus_id.bus_no if driver.bus_id else 'N/A',
                'latitude': str(driver.latitude),
                'longitude': str(driver.longitude),
                'last_updated': driver.last_updated.strftime('%Y-%m-%d %H:%M:%S') if driver.last_updated else 'Never'
            })

    return JsonResponse({
        'status': 'success',
        'buses': buses_data
    })
