""" 
created: 11/01/2019
author: marce
version: 
"""

from django import forms
from .models import Exemption


class RapidExemptionForm(forms.ModelForm):
    """Used in exemption panel to rapidly add an exemption of that patient."""
    class Meta:
        model = Exemption
        fields = ['patient', 'exemption', 'signature_place', 'signature_date']


