from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import *

# standard admin site.
admin.site.register(Patient)
admin.site.register(ExemptionCodes)
admin.site.register(Exemption)
admin.site.register(Place)
admin.site.register(Center)
admin.site.register(Analysis)
admin.site.register(AnalysisName)

# admin models
class AnalysisAdminModel(admin.ModelAdmin):
    radio_fields = {'rate': admin.HORIZONTAL}


class PatientsAdminModel(admin.ModelAdmin):
    radio_fields = {'sex': admin.HORIZONTAL}


class ExemptionAdminModel(admin.ModelAdmin):
    radio_fields = {'signature_place': admin.HORIZONTAL}


# custom admin for patients app
class PatientsAdmin(AdminSite):
    site_header = 'Djambu'
    site_title = 'djambu'
    site_url = '/patients/'
    index_title = 'amministrazione sito'

patients_admin = PatientsAdmin(name='patients_admin')
patients_admin.register(Patient, PatientsAdminModel)
patients_admin.register(Exemption, ExemptionAdminModel)
patients_admin.register(Analysis, AnalysisAdminModel)

