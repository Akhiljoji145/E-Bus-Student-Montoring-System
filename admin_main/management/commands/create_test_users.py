from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from student.models import student_details
from parent.models import parent
from teacher.models import teacher
from admin_main.models import admin_main
from management.models import management
from driver.models import Busdriver, Bus

class Command(BaseCommand):
    help = 'Create test users for all person types'

    def handle(self, *args, **options):
        try:
            # Create a test bus if not exists
            bus, created = Bus.objects.get_or_create(
                bus_no=1,
                defaults={
                    'bus_starting_point': 'School',
                    'bus_plate': 'MH12AB1234',
                    'departure_time': '08:00:00'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created test bus'))
            else:
                self.stdout.write('Test bus already exists')

            # Create test parent
            parent_obj, created = parent.objects.get_or_create(
                email='parent@test.com',
                defaults={
                    'name': 'Test Parent',
                    'password': make_password('password123'),
                    'phone_no': '1234567890'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created test parent'))
            else:
                self.stdout.write('Test parent already exists')

            # Create test student
            student, created = student_details.objects.get_or_create(
                email='student@test.com',
                defaults={
                    'name': 'Test Student',
                    'password': make_password('password123'),
                    'phone_no': '1234567891',
                    'stud_class': '10',
                    'branch': 'Science',
                    'accommodation_type': 'Day Scholar',
                    'bus': bus,
                    'parent': parent_obj
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created test student'))
            else:
                self.stdout.write('Test student already exists')

            # Create test teacher
            teacher_obj, created = teacher.objects.get_or_create(
                email='teacher@test.com',
                defaults={
                    'teacher_name': 'Test Teacher',
                    'password': make_password('password123'),
                    'class_no': '10',
                    'branch': 'Science',
                    'sem': '1'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created test teacher'))
            else:
                self.stdout.write('Test teacher already exists')

            # Create test admin_main
            admin, created = admin_main.objects.get_or_create(
                email='admin@test.com',
                defaults={
                    'name': 'Test Admin',
                    'password': make_password('password123'),
                    'phone_no': '1234567892'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created test admin'))
            else:
                self.stdout.write('Test admin already exists')

            # Create test management
            mgmt, created = management.objects.get_or_create(
                email='management@test.com',
                defaults={
                    'name': 'Test Management',
                    'password': make_password('password123'),
                    'phone_no': '1234567893'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created test management'))
            else:
                self.stdout.write('Test management already exists')

            # Create test driver
            driver, created = Busdriver.objects.get_or_create(
                email='driver@test.com',
                defaults={
                    'bus_driver': 'Test Driver',
                    'password': make_password('password123'),
                    'ph_no': '1234567894',
                    'bus_id': bus,
                    'status': 'permanent'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Created test driver'))
            else:
                self.stdout.write('Test driver already exists')

            self.stdout.write(self.style.SUCCESS('All test users created successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating test users: {str(e)}'))
            raise
