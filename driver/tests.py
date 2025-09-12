from django.test import TestCase, Client
from django.urls import reverse
from driver.models import Bus, Busdriver, StudentBoarding, BoardingAlert
from student.models import student_details
from django.utils import timezone

class DriverTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.bus = Bus.objects.create(bus_no=101, bus_starting_point='Start', bus_plate='ABC123')
        self.busdriver = Busdriver.objects.create(bus_driver='Driver1', email='driver1@example.com', password='pbkdf2_sha256$dummy', ph_no='1234567890', bus_id=self.bus)
        self.student = student_details.objects.create(name='Test Student', email='test@student.com', password='pbkdf2_sha256$dummy', bus=self.bus, stud_class='10', branch='A')
    
    def test_unregistered_alert_view(self):
        session = self.client.session
        session['id'] = self.busdriver.id
        session['bus_driver'] = self.busdriver.bus_driver
        session['email'] = self.busdriver.email
        session['bus_id'] = self.busdriver.bus_id.id
        session.save()
        response = self.client.get(reverse('driver:unregistered_alert'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Driver Alerts for Unregistered Students')

    def test_generate_qr_code_view(self):
        session = self.client.session
        session['id'] = self.busdriver.id
        session.save()
        response = self.client.get(reverse('driver:generate_qr_code', args=[self.bus.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QR Code for Bus')

    def test_mark_student_boarded(self):
        session = self.client.session
        session['id'] = self.busdriver.id
        session.save()
        boarding = StudentBoarding.objects.create(student=self.student, bus=self.bus, date=timezone.now().date(), status='not_boarded')
        response = self.client.post(reverse('driver:mark_student_boarded', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        boarding.refresh_from_db()
        self.assertEqual(boarding.status, 'boarded')
        alert = BoardingAlert.objects.filter(student=self.student, bus=self.bus, alert_type='boarded', sent_to='teacher').exists()
        self.assertTrue(alert)
