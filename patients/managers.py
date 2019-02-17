import datetime
from django.db.models import Manager
from patients import models
from .tools import TextToAnalysisTranslator


class AnalysisManager(Manager): # TODO: refactor functions

    translator = TextToAnalysisTranslator()

    def text_to_analysis(self, text: str, patient) -> None:
        analyses_data = self.translator.text_to_analysis(text)
        analyses = models.AnalysisName.objects.all()
        for data in analyses_data:
            analysis = data.pop('name')
            analysis_names = analyses.filter(name__startswith=analysis) | \
                analyses.filter(short_name__startswith=analysis)
            analysis_name = analysis_names.first()
            self.create(name=analysis_name, patient=patient, **data)
