from datetime import date
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


class TextToAnalysisTestCase(TestCase):

    def setUp(self):
        DATE = '01/01/2019'
        START_STRING = f'- {DATE} '
        TSH_ANALYTE = 'TSH'
        self.ONE_ANALYTE_RATE = START_STRING + TSH_ANALYTE + ' n'
        FSH_ANALYTE = 'FSH'
        self.ONE_ANALYTE_VALUE = START_STRING + FSH_ANALYTE + ' 3.15'
        TESTO_ANALYTE = 'testosterone'
        self.ONE_ANALYTE_VALUE_UNIT = START_STRING + TESTO_ANALYTE + ' 5.5 ng/dl'
        FT4_ANALYTE = 'FT4'
        self.ONE_ANALYTE_VALUE_UNIT_RANGE = START_STRING + FT4_ANALYTE + " 1.2 mmol/L (0.7-1.9)"
        FT3_ANALYTE = 'FT3'
        self.ONE_ANALYTE_VALUE_RANGE = START_STRING + FT3_ANALYTE + " 3.2 (2.4-6.2)"
        CORTISOL_ANALYTE = 'corti'
        self.ONE_ANALYTE_VALUE_HIGH_RANGE = START_STRING + CORTISOL_ANALYTE + " 19.1 (<22)"
        ACTH_ANALYTE = 'ACTH'
        self.ONE_ANALYTE_VALUE_LOW_RANGE = START_STRING + ACTH_ANALYTE + " 0.0 (>10)"

        self.MULTIPLE_ANALYTES = START_STRING + " TSH 3.15, FT4 n, FT3 n, corti 23.5 (<22.0), testo 2.4 ng/ml"

        AnalysisName.objects.create(name='tireotropina', short_name='TSH')
        AnalysisName.objects.create(name='levotiroxina libera', short_name='FT4')
        AnalysisName.objects.create(name='testosterone', short_name='testo')
        AnalysisName.objects.create(name='follitropina', short_name='FSH')
        AnalysisName.objects.create(name='tironina libera', short_name='FT3')
        AnalysisName.objects.create(name='cortisolo', short_name='corti')
        AnalysisName.objects.create(name='corticotropina', short_name='ACTH')

    def test_one_analyte_rate(self):
        Analysis.objects.text_to_analysis(self.ONE_ANALYTE_RATE)
        analysys = Analysis.objects.get(name__short_name='TSH')
        self.assertEqual(analysys.rate, 'n')

    def test_one_analyte_value(self):
        Analysis.objects.text_to_analysis(self.ONE_ANALYTE_VALUE)
        analysys = Analysis.objects.get(name__short_name='FSH')
        self.assertEqual(analysys.value, 3.15)

    def test_one_analyte_value_unit(self):
        Analysis.objects.text_to_analysis(self.ONE_ANALYTE_VALUE_UNIT)
        analysis = Analysis.objects.get(name__short_name='testo')
        self.assertEqual(analysis.unit, 'ng/dl')

    def test_one_analyte_value_unit_range(self):
        Analysis.objects.text_to_analysis(self.ONE_ANALYTE_VALUE_UNIT_RANGE)
        analysis = Analysis.objects.get(name__short_name='FT4')
        self.assertEqual(analysis.lower_limit, 0.7)
        self.assertEqual(analysis.upper_limit, 1.9)

    def test_one_analyte_value_range(self):
        Analysis.objects.text_to_analysis(self.ONE_ANALYTE_VALUE_RANGE)
        analysis = Analysis.objects.get(name__short_name='FT3')
        self.assertEqual(analysis.lower_limit, 2.4)
        self.assertEqual(analysis.upper_limit, 6.2)

    def test_one_analyte_value_range_high(self):
        Analysis.objects.text_to_analysis(self.ONE_ANALYTE_VALUE_HIGH_RANGE)
        analysis = Analysis.objects.get(name__short_name='corti')
        self.assertEqual(analysis.upper_limit, 22.0)
        self.assertIsNone(analysis.lower_limit)

    def test_one_analyte_value_range_low(self):
        Analysis.objects.text_to_analysis(self.ONE_ANALYTE_VALUE_LOW_RANGE)
        analysis = Analysis.objects.get(name__short_name='ACTH')
        self.assertEqual(analysis.lower_limit, 10.0)
        self.assertIsNone(analysis.upper_limit)

    def test_multiple_analytes(self):
        Analysis.objects.text_to_analysis(self.MULTIPLE_ANALYTES)
        print(Analysis.objects.all())




