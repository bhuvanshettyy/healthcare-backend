from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Patient, Doctor, PatientDoctor

User = get_user_model()


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'
        
    def validate_email(self, value):
        if Doctor.objects.filter(email=value).exists():
            if self.instance and self.instance.email == value:
                return value
            raise serializers.ValidationError("A doctor with this email already exists.")
        return value


class PatientSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    doctors = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_doctors(self, obj):
        doctors = [link.doctor for link in obj.doctor_links.all()]
        return DoctorSerializer(doctors, many=True).data
        
    def validate_age(self, value):
        if value is not None and (value < 0 or value > 150):
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('name', 'age', 'gender', 'notes')
        
    def validate_age(self, value):
        if value is not None and (value < 0 or value > 150):
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value


class PatientDoctorSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    
    class Meta:
        model = PatientDoctor
        fields = '__all__'
        read_only_fields = ('created_at',)
        
    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')
        
        if PatientDoctor.objects.filter(patient=patient, doctor=doctor).exists():
            if not self.instance:  # Only check for creation, not updates
                raise serializers.ValidationError("This patient is already assigned to this doctor.")
        
        return attrs


class AssignDoctorSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    
    def validate_doctor_id(self, value):
        try:
            Doctor.objects.get(id=value)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError("Doctor with this ID does not exist.")
        return value


class PatientDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    assigned_doctors = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')
    
    def get_assigned_doctors(self, obj):
        doctor_links = obj.doctor_links.all()
        doctors = [link.doctor for link in doctor_links]
        return DoctorSerializer(doctors, many=True).data


class DoctorDetailSerializer(serializers.ModelSerializer):
    assigned_patients = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_assigned_patients(self, obj):
        patient_links = obj.patient_links.all()
        patients = [link.patient for link in patient_links]
        return PatientSerializer(patients, many=True).data