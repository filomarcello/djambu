from django.test import TestCase
from patients.models import *
from random import random


class AnalysisTestCase(TestCase):
    def setUp(self):
        for name, short_name in zip(
                ['testosterone', 'paratormone', 'tireotropina', 'tiroxina libera', 'tironina libera'],
                ['testo', 'PTH', 'TSH', 'FT4', 'FT3']):
            AnalysisName.objects.create(name=name, short_name=short_name)

        testo = Analysis(name=AnalysisName.objects.get(short_name='testo'))
        testo.value = 115.0
        testo.lower_limit=2.4
        testo.upper_limit=8.3
        testo.save()

        pth = Analysis(name=AnalysisName.objects.get(short_name='PTH'))
        pth.value=100
        pth.lower_limit=50
        pth.upper_limit=150
        pth.rate=RATINGS['normale']
        pth.save()

        tsh = Analysis(name=AnalysisName.objects.get(short_name='TSH'))
        tsh.value=100
        tsh.lower_limit=50
        tsh.upper_limit=150
        tsh.save()

        ft4 = Analysis(name=AnalysisName.objects.get(short_name='FT4'))
        ft4.value=100
        ft4.lower_limit=50
        ft4.upper_limit=150
        ft4.save()

        ft3 = Analysis(name=AnalysisName.objects.get(short_name='FT3'))
        ft3.value=100
        ft3.rate=RATINGS['normale']
        ft3.save()

    def test_value(self):
        testo = Analysis.objects.get(name__short_name='testo')
        self.assertEqual(testo.value, 115.0)

    def test_rate(self):
        tsh = Analysis.objects.get(name__short_name='TSH')
        self.assertEqual(tsh.rating(), RATINGS['normale'])

    def test_limits(self):
        testo = Analysis.objects.get(name__short_name='testo')
        self.assertEqual(testo.lower_limit, 2.4)
        self.assertEqual(testo.upper_limit, 8.3)

    def test_rating_when_rate_is_set_by_user(self):
        pth = Analysis.objects.get(name__short_name='PTH')
        self.assertEqual(pth.rating(), 'n')




