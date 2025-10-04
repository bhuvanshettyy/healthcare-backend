from django.contrib import admin
from .models import Patient, Doctor, PatientDoctor

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "age", "gender", "created_by", "created_at")
    search_fields = ("name", "created_by__email")
    list_filter = ("gender", "created_at")

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "specialization", "email")
    search_fields = ("name", "email", "specialization")

@admin.register(PatientDoctor)
class PatientDoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "created_at")
    search_fields = ("patient__name", "doctor__name", "doctor__email")
