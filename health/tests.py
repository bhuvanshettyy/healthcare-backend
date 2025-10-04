from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse
from .models import Patient, Doctor, PatientDoctor

User = get_user_model()


class HealthModelTestCase(TestCase):
    """Test health app models"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_patient_creation(self):
        """Test patient model creation"""
        patient = Patient.objects.create(
            name='John Doe',
            age=30,
            gender='Male',
            notes='Test patient',
            created_by=self.user
        )
        self.assertEqual(str(patient), 'John Doe (id=1)')
        self.assertEqual(patient.created_by, self.user)
    
    def test_doctor_creation(self):
        """Test doctor model creation"""
        doctor = Doctor.objects.create(
            name='Dr. Smith',
            specialization='Cardiology',
            email='dr.smith@hospital.com',
            phone='123-456-7890'
        )
        self.assertEqual(str(doctor), 'Dr. Dr. Smith')
        self.assertEqual(doctor.email, 'dr.smith@hospital.com')
    
    def test_patient_doctor_relationship(self):
        """Test patient-doctor relationship"""
        patient = Patient.objects.create(
            name='John Doe',
            age=30,
            created_by=self.user
        )
        doctor = Doctor.objects.create(
            name='Dr. Smith',
            email='dr.smith@hospital.com'
        )
        
        relationship = PatientDoctor.objects.create(
            patient=patient,
            doctor=doctor
        )
        
        self.assertEqual(relationship.patient, patient)
        self.assertEqual(relationship.doctor, doctor)


class PatientAPITestCase(APITestCase):
    """Test Patient API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        
        self.patient_data = {
            'name': 'John Doe',
            'age': 30,
            'gender': 'Male',
            'notes': 'Test patient'
        }
        
        self.patients_url = reverse('health:patient-list')
    
    def authenticate(self, user=None):
        """Helper method to authenticate requests"""
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_patient_authenticated(self):
        """Test creating a patient when authenticated"""
        self.authenticate()
        response = self.client.post(self.patients_url, self.patient_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Patient.objects.filter(name='John Doe').exists())
        
        # Verify patient is created by the authenticated user
        patient = Patient.objects.get(name='John Doe')
        self.assertEqual(patient.created_by, self.user)
    
    def test_create_patient_unauthenticated(self):
        """Test creating a patient when not authenticated"""
        response = self.client.post(self.patients_url, self.patient_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_patients_own_only(self):
        """Test that users can only see their own patients"""
        # Create patients for different users
        Patient.objects.create(name='User1 Patient', created_by=self.user)
        Patient.objects.create(name='User2 Patient', created_by=self.other_user)
        
        self.authenticate(self.user)
        response = self.client.get(self.patients_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only see own patient
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'User1 Patient')
    
    def test_update_patient(self):
        """Test updating a patient"""
        patient = Patient.objects.create(
            name='John Doe',
            age=30,
            created_by=self.user
        )
        
        self.authenticate()
        update_data = {'name': 'John Updated', 'age': 31}
        response = self.client.patch(
            reverse('health:patient-detail', args=[patient.id]),
            update_data
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient.refresh_from_db()
        self.assertEqual(patient.name, 'John Updated')
        self.assertEqual(patient.age, 31)
    
    def test_delete_patient(self):
        """Test deleting a patient"""
        patient = Patient.objects.create(
            name='John Doe',
            created_by=self.user
        )
        
        self.authenticate()
        response = self.client.delete(
            reverse('health:patient-detail', args=[patient.id])
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(id=patient.id).exists())


class DoctorAPITestCase(APITestCase):
    """Test Doctor API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.doctor_data = {
            'name': 'Dr. Smith',
            'specialization': 'Cardiology',
            'email': 'dr.smith@hospital.com',
            'phone': '123-456-7890'
        }
        
        self.doctors_url = reverse('health:doctor-list')
    
    def authenticate(self):
        """Helper method to authenticate requests"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_doctor_authenticated(self):
        """Test creating a doctor when authenticated"""
        self.authenticate()
        response = self.client.post(self.doctors_url, self.doctor_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Doctor.objects.filter(email='dr.smith@hospital.com').exists())
    
    def test_create_doctor_duplicate_email(self):
        """Test creating a doctor with duplicate email"""
        Doctor.objects.create(
            name='Dr. Existing',
            email='dr.smith@hospital.com'
        )
        
        self.authenticate()
        response = self.client.post(self.doctors_url, self.doctor_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_doctors(self):
        """Test listing all doctors"""
        Doctor.objects.create(name='Dr. Smith', email='dr1@hospital.com')
        Doctor.objects.create(name='Dr. Jones', email='dr2@hospital.com')
        
        self.authenticate()
        response = self.client.get(self.doctors_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)


class PatientDoctorRelationshipTestCase(APITestCase):
    """Test patient-doctor relationship management"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.patient = Patient.objects.create(
            name='John Doe',
            age=30,
            created_by=self.user
        )
        
        self.doctor = Doctor.objects.create(
            name='Dr. Smith',
            email='dr.smith@hospital.com'
        )
    
    def authenticate(self):
        """Helper method to authenticate requests"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_assign_doctor_to_patient(self):
        """Test assigning a doctor to a patient"""
        self.authenticate()
        
        url = reverse('health:patient-assign-doctor', args=[self.patient.id])
        data = {'doctor_id': self.doctor.id}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify relationship was created
        self.assertTrue(
            PatientDoctor.objects.filter(
                patient=self.patient, 
                doctor=self.doctor
            ).exists()
        )
    
    def test_assign_nonexistent_doctor(self):
        """Test assigning a nonexistent doctor to a patient"""
        self.authenticate()
        
        url = reverse('health:patient-assign-doctor', args=[self.patient.id])
        data = {'doctor_id': 999}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unassign_doctor_from_patient(self):
        """Test unassigning a doctor from a patient"""
        # First assign the doctor
        PatientDoctor.objects.create(patient=self.patient, doctor=self.doctor)
        
        self.authenticate()
        
        url = reverse('health:patient-unassign-doctor', args=[self.patient.id])
        data = {'doctor_id': self.doctor.id}
        
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify relationship was deleted
        self.assertFalse(
            PatientDoctor.objects.filter(
                patient=self.patient, 
                doctor=self.doctor
            ).exists()
        )
