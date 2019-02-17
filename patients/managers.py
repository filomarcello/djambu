from django.db.models import Manager
from patients import models
from .tools import TextToAnalysisTranslator


class AnalysisManager(Manager):

    translator = TextToAnalysisTranslator() # TODO: maybe yet too ugly...

    def text_to_analysis(self, text: str, patient) -> None:
        analyses_data = self.translator.text_to_analysis(text)
        analyses_names = models.AnalysisName.objects.all()
        for data in analyses_data:
            analysis = data.pop('name')
            analysis_name = analyses_names.filter(name__startswith=analysis) | \
                analyses_names.filter(short_name__startswith=analysis)
            name = analysis_name.first()
            self.create(name=name, patient=patient, **data)
