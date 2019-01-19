from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import *

# standard admin site.
admin.site.register(Patient)
admin.site.register(ExemptionCodes)
admin.site.register(Exemption)
admin.site.register(Place)

# custom admin for patients app
class PatientsAdmin(AdminSite):
    site_header = 'Djambu'
    site_title = 'djambu'
    site_url = '/patients/'
    index_title = 'Amministrazione sito'

patients_admin = PatientsAdmin(name='patients_admin')
patients_admin.register(Patient)
patients_admin.register(Exemption)

