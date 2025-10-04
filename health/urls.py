from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, DoctorViewSet, PatientDoctorViewSet

app_name = 'health'

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'patient-doctors', PatientDoctorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]