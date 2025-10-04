from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Patient, Doctor, PatientDoctor
from .serializers import (
    PatientSerializer,
    PatientCreateSerializer,
    PatientDetailSerializer,
    DoctorSerializer,
    DoctorDetailSerializer,
    PatientDoctorSerializer,
    AssignDoctorSerializer
)


class PatientViewSet(viewsets.ModelViewSet):
    """CRUD operations for patients"""
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'created_by']
    search_fields = ['name', 'notes']
    ordering_fields = ['name', 'age', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PatientCreateSerializer
        elif self.action == 'retrieve':
            return PatientDetailSerializer
        return PatientSerializer
    
    def get_queryset(self):
        # Avoid DB filters during schema generation or unauthenticated access
        if getattr(self, "swagger_fake_view", False):
            return Patient.objects.none()
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return Patient.objects.none()
        # Users can only see their own patients
        return Patient.objects.filter(created_by=user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assign_doctor(self, request, pk=None):
        """Assign a doctor to a patient"""
        patient = self.get_object()
        serializer = AssignDoctorSerializer(data=request.data)
        
        if serializer.is_valid():
            doctor_id = serializer.validated_data['doctor_id']
            doctor = get_object_or_404(Doctor, id=doctor_id)
            
            # Check if assignment already exists
            if PatientDoctor.objects.filter(patient=patient, doctor=doctor).exists():
                return Response(
                    {'error': 'This doctor is already assigned to this patient'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            PatientDoctor.objects.create(patient=patient, doctor=doctor)
            return Response(
                {'message': f'Doctor {doctor.name} assigned to patient {patient.name}'},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def unassign_doctor(self, request, pk=None):
        """Unassign a doctor from a patient"""
        patient = self.get_object()
        doctor_id = request.data.get('doctor_id')
        
        if not doctor_id:
            return Response(
                {'error': 'doctor_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            assignment = PatientDoctor.objects.get(patient=patient, doctor=doctor)
            assignment.delete()
            
            return Response(
                {'message': f'Doctor {doctor.name} unassigned from patient {patient.name}'},
                status=status.HTTP_200_OK
            )
        except Doctor.DoesNotExist:
            return Response(
                {'error': 'Doctor not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PatientDoctor.DoesNotExist:
            return Response(
                {'error': 'This doctor is not assigned to this patient'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DoctorViewSet(viewsets.ModelViewSet):
    """CRUD operations for doctors"""
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization']
    search_fields = ['name', 'email', 'specialization']
    ordering_fields = ['name', 'specialization', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DoctorDetailSerializer
        return DoctorSerializer
    
    @action(detail=True, methods=['get'])
    def patients(self, request, pk=None):
        """Get all patients assigned to this doctor"""
        doctor = self.get_object()
        patient_links = PatientDoctor.objects.filter(doctor=doctor)
        patients = [link.patient for link in patient_links]
        
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)


class PatientDoctorViewSet(viewsets.ModelViewSet):
    """Manage patient-doctor relationships"""
    queryset = PatientDoctor.objects.all()
    serializer_class = PatientDoctorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'doctor']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Avoid DB filters during schema generation or unauthenticated access
        if getattr(self, "swagger_fake_view", False):
            return PatientDoctor.objects.none()
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return PatientDoctor.objects.none()
        # Users can only see relationships for their own patients
        return PatientDoctor.objects.filter(patient__created_by=user)
