from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Busdriver, Bus, StudentBoarding, BusMessage
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
    ist_tz = pytz.timezone('Asia/Kolkata')

    # Get or create StudentBoarding for registered students
    registered_students = hosteler_reg.objects.filter(bus=bus.bus_no)
    for reg in registered_students:
        StudentBoarding.objects.get_or_create(
            student=reg.student_id,
            bus=bus,
            date=today,
            defaults={'status': 'not_boarded'}
        )

    # Get alerts for driver - unboarded students
    unboarded_alerts = StudentBoarding.objects.filter(bus=bus, date=today, status='not_boarded').order_by('student__name')
    filtered_alerts = []
    for alert in unboarded_alerts:
        # Exclude students who have neither morning nor evening scan (considered absent)
        if not alert.morning_scan and not alert.evening_scan:
            continue
        if not alert.morning_scan:
            alert.display_type = 'morning'
        elif alert.morning_scan and not alert.evening_scan:
            alert.display_type = 'evening'
        else:
            alert.display_type = 'unknown'
        filtered_alerts.append(alert)
    unboarded_alerts = filtered_alerts

    # Get boarding alerts from StudentBoarding model
    boarding_records = StudentBoarding.objects.filter(bus=bus, date=today, status='boarded').order_by('-time')
    boarding_alerts = []
    for record in boarding_records:
        if record.morning_scan and not record.evening_scan:
            display_type = 'morning'
        elif record.evening_scan:
            display_type = 'evening'
        else:
            display_type = 'unknown'
        boarding_alerts.append({
            'student': record.student,
            'display_type': display_type,
            'sent_at': record.time,
            'date': record.date
        })
    students = StudentBoarding.objects.filter(bus=bus, date=today)  # Show all boarding records for today
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
            'morning_scan': student_boarding.morning_scan,
            'morning_latitude': student_boarding.morning_latitude,
            'morning_longitude': student_boarding.morning_longitude,
            'evening_scan': student_boarding.evening_scan,
            'evening_latitude': student_boarding.evening_latitude,
            'evening_longitude': student_boarding.evening_longitude,
        })

    hostelers = hosteler_reg.objects.filter(bus=bus.bus_no)  # Get registered hosteler students for the bus

    # Get bus messages sent by this driver
    bus_messages = BusMessage.objects.filter(driver=driver).order_by('-sent_at')

    context = {
        'driver': driver,
        'bus': bus,
        'unboarded_alerts': unboarded_alerts,
        'boarding_alerts': boarding_alerts,
        'students': students_with_ist_time,
        'hostelers': hostelers,
        'bus_messages': bus_messages,
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
            ist_tz = pytz.timezone('Asia/Kolkata')
            current_time_ist = timezone.now().astimezone(ist_tz).time()
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            # Define scanning time windows
            morning_start = datetime.strptime('05:00:00', '%H:%M:%S').time()
            morning_end = datetime.strptime('12:00:00', '%H:%M:%S').time()
            evening_start = datetime.strptime('15:00:00', '%H:%M:%S').time()
            evening_end = datetime.strptime('20:00:00', '%H:%M:%S').time()

            # Check if current time is within allowed scanning windows
            if morning_start <= current_time_ist <= morning_end:
                is_morning_scan = True
            elif evening_start <= current_time_ist <= evening_end:
                is_morning_scan = False
            else:
                return JsonResponse({'status': 'error', 'message': 'Boarding not allowed at this time'})

            boarding = StudentBoarding.objects.get(student_id=student_id, bus=bus, date=today)

            # Check if student has already scanned for this session
            if is_morning_scan and boarding.morning_scan:
                return JsonResponse({'status': 'error', 'message': 'You have already scanned for morning session today'})
            elif not is_morning_scan and boarding.evening_scan:
                return JsonResponse({'status': 'error', 'message': 'You have already scanned for evening session today'})

            if is_morning_scan:
                boarding.morning_scan = True
                if latitude and longitude:
                    boarding.morning_latitude = latitude
                    boarding.morning_longitude = longitude
            else:
                boarding.evening_scan = True
                if latitude and longitude:
                    boarding.evening_latitude = latitude
                    boarding.evening_longitude = longitude
            boarding.status = 'boarded'
            boarding.time = timezone.now().time()
            boarding.save()
            alert_type = 'boarded_morning' if is_morning_scan else 'boarded_evening'
            return JsonResponse({'status': 'success', 'message': f'Successfully boarded for {"morning" if is_morning_scan else "evening"} session'})
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
