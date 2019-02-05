""" 
patients urls
"""

from django.urls import path
from .views import *

app_name = 'patients'
urlpatterns = [
    path('', HomeView.as_view(),
         name='home'),
    path('<int:pk>/', PatientDetailView.as_view(),
         name='patient_detail'),
    path('<int:pk>', PatientExemptionsView.as_view(),
         name='patient_exemptions_list'),
    path('rapid_add_exemption/', RapidAddExemptionView.as_view(),
         name='rapid_add_exemption'),
    path('list/', PatientsListView.as_view(),
         name='patients_list'),
    path('prova_pdf/<int:pk>', PDFResponseView.as_view(),
         name='exemption_pdf')
]
