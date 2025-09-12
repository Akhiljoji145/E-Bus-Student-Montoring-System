from django.test import TestCase, Client
from django.urls import reverse
from driver.models import Bus, Busdriver, StudentBoarding, BoardingAlert
from student.models import student_details
from django.utils import timezone

class BoardingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.bus = Bus.objects.create(bus_no=101, bus_starting_point='Start', bus_plate='ABC123')
        self.student = student_details.objects.create(name='Test Student', email='test@student.com', password='pbkdf2_sha256$dummy', bus=self.bus, stud_class='10', branch='A')
        self.busdriver = Busdriver.objects.create(bus_driver='Driver1', email='driver1@example.com', password='pbkdf2_sha256$dummy', ph_no='1234567890', bus_id=self.bus)
    
    def test_qr_scan_page(self):
        response = self.client.get(reverse('student:qr_scan'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Scan QR Code')

    def test_handle_boarding_registered_student(self):
        url = reverse('student:handle_boarding', args=[self.bus.id])
        response = self.client.post(url, {'student_id': self.student.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Boarding Successful!')
        boarding = StudentBoarding.objects.filter(student=self.student, bus=self.bus, date=timezone.now().date()).first()
        self.assertIsNotNone(boarding)
        self.assertEqual(boarding.status, 'boarded')
        alert = BoardingAlert.objects.filter(student=self.student, bus=self.bus, alert_type='boarded', sent_to='teacher').exists()
        self.assertTrue(alert)

    def test_handle_boarding_unregistered_student(self):
        other_bus = Bus.objects.create(bus_no=102, bus_starting_point='Other', bus_plate='XYZ789')
        url = reverse('student:handle_boarding', args=[other_bus.id])
        response = self.client.post(url, {'student_id': self.student.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student not registered for this bus')
        alert = BoardingAlert.objects.filter(student=self.student, bus=other_bus, alert_type='unregistered', sent_to='driver').exists()
        self.assertTrue(alert)
