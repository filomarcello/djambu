import io

from django.http import FileResponse, HttpResponse
from django.views.generic import TemplateView, ListView, DetailView, \
    FormView
from django.urls import reverse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph

from .forms import RapidExemptionForm
from .models import Patient, Exemption


class HomeView(TemplateView):
    template_name = 'patients/home.html'


class PatientsListView(ListView):
    model = Patient
    template_name = 'patients/patients_list.html'


class PatientDetailView(DetailView):
    model = Patient
    template_name = 'patients/patient_detail.html'

    def get_context_data(self, **kwargs):
        """Pass the patient to the template and also other data."""
        context = super().get_context_data(**kwargs)
        context['exemptions'] = Exemption.objects.filter(
                patient_id=self.object.pk)
        # make an unbound RapidExemptionForm form
        context['exemption_form'] = RapidExemptionForm()
        # context['plans'] =
        # context['visits'] =
        return context


class PatientExemptionsView(ListView):
    """Return the exemptions linked to a patient."""
    model = Exemption
    template_name = 'patients/exemptions_detail.html'


class RapidAddExemptionView(FormView):
    """Display the RapidExemption form."""
    template_name = 'rapid_exemption_form.html'
    form_class = RapidExemptionForm
    success_url = '/patients'

    def form_valid(self, form):
        pat = form.cleaned_data['patient']
        exe = form.cleaned_data['exemption']
        sign_pla = form.cleaned_data['signature_place']
        sign_dat = form.cleaned_data['signature_date']
        e = Exemption(patient=pat, exemption=exe, signature_place=sign_pla,
                  signature_date=sign_dat)
        e.save()
        self.success_url = reverse('patients:patient_detail', args=[pat.pk])
        return super().form_valid(form)


def print_exemption_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="prova.pdf'
    doc = SimpleDocTemplate(response)
    normal = ParagraphStyle(name='normal', fontName='Helvetica', fontSize=12)
    story = [
        Paragraph("Ciao pipposi!!!", normal),
        Spacer(1, 5*cm),
        Paragraph("Mo funzia!", normal)
    ]
    doc.build(story)
    return response


    
