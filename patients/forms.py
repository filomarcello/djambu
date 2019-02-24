from django import forms
from .models import Exemption


class RapidExemptionForm(forms.ModelForm):
    """Used in exemption panel to rapidly add an exemption of that patient."""
    class Meta:
        model = Exemption
        fields = ['patient', 'exemption', 'signature_place', 'signature_date']


class TextToAnalysisForm(forms.Form):
    """Used to quickly translate a string in Analysis objects."""
    text = forms.CharField()
    patient = forms.CharField()
