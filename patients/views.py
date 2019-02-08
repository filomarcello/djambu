import io

from django.http import FileResponse, HttpResponse
from django.views.generic import TemplateView, ListView, DetailView, \
    FormView
from django.urls import reverse
from django.views.generic.base import TemplateResponseMixin, View
from reportlab.lib.enums import TA_CENTER
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
        e.full_clean()
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


class PDFResponseView(DetailView):

    model = Exemption

    def render_to_response(self, context, **response_kwargs):
        return self.make_pdf()

    def make_pdf(self):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="prova{}.pdf'.format(self.object.pk)

        doc = SimpleDocTemplate(response, pageSize=A4)
        name = self.object.name.upper()
        birth_place = self.object.birth_place.capitalize()
        birth_date = self.object.birth_date
        exemption_name = self.object.exemption.name.title()
        exemption_code = self.object.exemption.code
        place = self.object.signature_place.municipality.capitalize()
        date = self.object.signature_date

        normal = ParagraphStyle(name='normal', fontName='Helvetica', fontSize=12)
        label = ParagraphStyle(name='label', parent=normal, fontName='Helvetica-Bold',
                               leading=20)
        center_label = ParagraphStyle(name='center_label', parent=label,
                                      alignment=TA_CENTER)
        notes = ParagraphStyle(name='notes', parent=normal, fontSize=8)
        code = ParagraphStyle(name='code', fontName='Courier-Bold', fontSize=30,
                              leading=36)
        exemption = ParagraphStyle(name='exemption', parent=label, fontSize=14,
                                   alignment=TA_CENTER, leading=20)

        story = []
        story.append(Paragraph("Regione Lombardia", center_label))

        story.append(Spacer(1, 3 * cm))

        story.append(Paragraph("CERTIFICAZIONE", center_label))
        story.append(Paragraph('ai sensi dell’art.4, '
                               'comma 1 del Decreto Ministero Sanità 28 maggio 1999, '
                               'n. 329 “Regolamento recante norme di individuazione '
                               'delle malattie croniche e invalidanti ai sensi dell’'
                               'articolo 5, comma 1, lettera a) del decreto legislativo'
                               ' 29 aprile 1998, n. 124”, come modificato dal Decreto '
                               'Ministero Sanità 21 maggio 2001 n. 296 “Regolamento di '
                               'aggiornamento del decreto ministeriale 28 maggio 1999, '
                               'n 329...”', notes))

        story.append(Spacer(1, 1 * cm))

        story.append(Paragraph(f'Si certifica che la/il Sig.ra/re <i>{name}</i>', label))
        story.append(Paragraph(f"nata/o a <i>{birth_place}</i>", label))
        story.append(Paragraph(f"in data <i>{birth_date}</i>", label))

        story.append(Spacer(1, 0.5 * cm))

        story.append(Paragraph("È affetta/o dalla seguente patologia", center_label))
        story.append(Paragraph("(descrivere la patologia come riportato nell’elenco di "
                               "cui all’Allegato 1-II parte del D.M. 329/99 come "
                               "modificato dal D.M. 296/2001).", notes))

        # story.append(Spacer(1, 0.5*cm))

        story.append(Paragraph(f'<i>{exemption_name}</i>', exemption))

        story.append(Paragraph("(N.B.: in caso di IPERTENSIONE ARTERIOSA specificare "
                               "CON DANNO D’ORGANO quando presente, in riferimento alle"
                               " Linee Guida dell’O.M.S)", notes))

        story.append(Spacer(1, 0.5 * cm))

        story.append(Paragraph("Contraddistinta dal Codice", center_label))
        story.append(Paragraph("(riportare il Codice di cui all’Allegato 1-II parte del"
                               " D.M. 329/99 come modificato dal D.M. \
        296/2001)", notes))

        story.append(Spacer(1, 0.2 * cm))

        story.append(Paragraph(f"{exemption_code}", code))
        story.append(Paragraph("(Cod. progressivo) (Cod. I.C.D.9-C.M.)", notes))

        story.append(Spacer(1, 1.5 * cm))

        story.append(Paragraph(f"{place}, {date}", label))

        story.append(Spacer(1, 1.5 * cm))

        story.append(Paragraph("Timbro e firma del Medico", label))

        doc.build(story)

        return response

    
