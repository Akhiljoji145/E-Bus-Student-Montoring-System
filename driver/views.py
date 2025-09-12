from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Busdriver, Bus, StudentBoarding, BoardingAlert, BusMessage
from student.models import hosteler_reg, student_details
from django.contrib.sessions.models import Session
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta, datetime
import pytz
from .utils import generate_bus_qr_code

# Create your views here.
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            busdriver_login = Busdriver.objects.get(email=email)
            if check_password(password, busdriver_login.password):
                request.session['id'] = busdriver_login.id
                request.session['bus_driver'] = busdriver_login.bus_driver
                request.session['email'] = busdriver_login.email
                request.session['bus_id'] = busdriver_login.bus_id.id
                return redirect('driver:dashboard')
            else:
                messages.error(request, 'Invalid email or password')
                return render(request, 'driver_login.html')
        except Busdriver.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'driver_login.html')
    return render(request, 'driver_login.html')

def login_dashboard(request):
    return redirect('/login_dashboard')

def dashboard(request):
    if 'id' not in request.session:
        return redirect('driver:login')
    driver_id = request.session['id']
    driver = Busdriver.objects.get(id=driver_id)
    bus = driver.bus_id
    today = timezone.now().date()
    current_time = timezone.now().time()

    # Get or create StudentBoarding for registered students
    registered_students = hosteler_reg.objects.filter(bus=bus.bus_no)
    for reg in registered_students:
        StudentBoarding.objects.get_or_create(
            student=reg.student_id,
            bus=bus,
            date=today,
            defaults={'status': 'not_boarded'}
        )

    # Check for alerts 5 mins before departure
    if bus.departure_time:
        alert_time = (timezone.datetime.combine(today, bus.departure_time) - timedelta(minutes=5)).time()
        if current_time >= alert_time:
            unboarded = StudentBoarding.objects.filter(bus=bus, date=today, status='not_boarded', alert_sent=False)
            for boarding in unboarded:
                BoardingAlert.objects.get_or_create(
                    student=boarding.student,
                    bus=bus,
                    alert_type='not_boarded',
                    sent_to='teacher',
                    defaults={'sent_at': timezone.now()}
                )
                BoardingAlert.objects.get_or_create(
                    student=boarding.student,
                    bus=bus,
                    alert_type='not_boarded',
                    sent_to='driver',
                    defaults={'sent_at': timezone.now()}
                )
                boarding.alert_sent = True
                boarding.save()

    # Get alerts for driver
    alerts = BoardingAlert.objects.filter(bus=bus, sent_to='driver', sent_at__date=today).order_by('-sent_at')
    students = StudentBoarding.objects.filter(bus=bus, date=today, status='boarded')  # Show only students currently in the bus
    ist_tz = pytz.timezone('Asia/Kolkata')
    students_with_ist_time = []
    for student_boarding in students:
        boarding_time = student_boarding.time
        if boarding_time:
            utc_dt = datetime.combine(today, boarding_time, tzinfo=pytz.utc)
            ist_dt = utc_dt.astimezone(ist_tz)
            boarding_time_ist = ist_dt.time()
        else:
            boarding_time_ist = None
        students_with_ist_time.append({
            'student': student_boarding.student,
            'status': student_boarding.status,
            'boarding_time': boarding_time_ist,
        })

    hostelers = hosteler_reg.objects.filter(bus=bus.bus_no)  # Get registered hosteler students for the bus

    context = {
        'driver': driver,
        'bus': bus,
        'alerts': alerts,
        'students': students_with_ist_time,
        'hostelers': hostelers,
    }
    return render(request, 'driver_dashboard.html', context)

def logout(request):
    request.session.flush()
    return redirect('student:login_dashboard')

def mark_student_boarded(request, student_id):
    if request.method == 'POST':
        try:
            driver = Busdriver.objects.get(id=request.session['id'])
            bus = driver.bus_id
            today = timezone.now().date()
            boarding = StudentBoarding.objects.get(student_id=student_id, bus=bus, date=today)
            boarding.status = 'boarded'
            boarding.time = timezone.now().time()
            boarding.save()
            # Send alert to teacher
            BoardingAlert.objects.create(
                student=boarding.student,
                bus=bus,
                alert_type='boarded',
                sent_to='teacher'
            )
            return JsonResponse({'status': 'success'})
        except StudentBoarding.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Student not found'})
    return JsonResponse({'status': 'error'})

def send_bus_change_message(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        audience = request.POST.get('audience')
        parent_contact = request.POST.get('parent_contact', '')
        driver = Busdriver.objects.get(id=request.session['id'])
        BusMessage.objects.create(
            driver=driver,
            subject=subject,
            message=message,
            audience=audience,
            parent_contact=parent_contact
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def validate_departure(request):
    if request.method == 'POST':
        driver = Busdriver.objects.get(id=request.session['id'])
        bus = driver.bus_id
        today = timezone.now().date()
        missing = StudentBoarding.objects.filter(bus=bus, date=today, status='not_boarded').count()
        if missing > 0:
            return JsonResponse({'status': 'error', 'message': f'{missing} students missing'})
        else:
            StudentBoarding.objects.filter(bus=bus, date=today, status='boarded').update(status='departed')
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def unregistered_alert(request):
    if 'id' not in request.session:
        return redirect('driver:login')
    driver_id = request.session['id']
    driver = Busdriver.objects.get(id=driver_id)
    bus = driver.bus_id
    today = timezone.now().date()

    # Get unregistered alerts for the driver
    alerts = BoardingAlert.objects.filter(bus=bus, sent_to='driver', alert_type='unregistered', sent_at__date=today).order_by('-sent_at')

    context = {
        'driver': driver,
        'bus': bus,
        'alerts': alerts,
    }
    return render(request, 'driver_alert.html', context)

def generate_qr_code(request, bus_id):
    if 'id' not in request.session:
        return redirect('driver:login')
    driver = Busdriver.objects.get(id=request.session['id'])
    if driver.bus_id.id != bus_id:
        return redirect('driver:dashboard')
    
    from .utils import generate_bus_qr_code
    # Ensure base_url ends with a slash
    base_url = request.build_absolute_uri('/')
    if not base_url.endswith('/'):
        base_url += '/'
    qr_code = generate_bus_qr_code(bus_id, base_url)
    
    context = {
        'qr_code': qr_code,
        'bus': driver.bus_id,
    }
    return render(request, 'qr_code_display.html', context)
