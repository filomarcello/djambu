from django.test import TestCase
from patients.models import *
from random import random


class AnalysisTestCase(TestCase):
    def setUp(self):
        Analysis.objects.create(name='TSH')
        Analysis.objects.create(name='glicemia', value=115.0)
        for i, rate in enumerate(RATINGS.values(), start=1):
            Analysis.objects.create(name='gpt'+str(i), rate=rate)
        Analysis.objects.create(name='got', rate=RATINGS['limite inferiore']
        )
        Analysis.objects.create(
                name='testosterone',
                lower_limit=2.4,
                upper_limit=8.3
        )
        Analysis.objects.create(
                name='sticchiotropina',
                value=100,
                lower_limit=50,
                upper_limit=150,
                rate=RATINGS['normale'],
        )
        Analysis.objects.create(
                name='minchiotropina',
                value=100,
                lower_limit=50,
                upper_limit=150,
        )
        Analysis.objects.create(
                name='culotropina',
                value=100,
                lower_limit=50,
                upper_limit=150,
        )
        Analysis.objects.create(
                name='puzzotropina',
                value=100,
                rate=RATINGS['normale']
        )

    def test_default_creation(self):
        tsh = Analysis.objects.get(name='TSH')

    def test_value(self):
        glice = Analysis.objects.get(name='glicemia')
        self.assertEqual(glice.value, 115.0)

    def test_rate(self):
        gpts = Analysis.objects.filter(name__startswith='gpt')
        self.assertIsNot(len(gpts), 0)
        for gpt, rate in zip(gpts, RATINGS.values()):
            self.assertEqual(gpt.rate, rate)
        got = Analysis.objects.get(name='got')
        self.assertEqual(got.rate, 'li')

    def test_limits(self):
        testo = Analysis.objects.get(name='testosterone')
        self.assertEqual(testo.lower_limit, 2.4)
        self.assertEqual(testo.upper_limit, 8.3)

    def test_rating_when_rate_is_set_by_user(self):
        st = Analysis.objects.get(name='sticchiotropina')
        self.assertEqual(st.rating(), 'n')

    def test_rating_when_rate_and_limits_not_set(self):
        ct = Analysis.objects.get(name='culotropina')
        ct.lower_limit = None
        self.assertIsNone(ct.rating())
        ct.lower_limit = 100.0
        ct.upper_limit = None
        self.assertIsNone(ct.rating())
        ct.lower_limit = None
        ct.upper_limit = None
        self.assertIsNone(ct.rating())

    def test_rating_when_rate_not_user_set(self):
        mt = Analysis.objects.get(name='minchiotropina')
        range = mt.upper_limit - mt.lower_limit
        tolerance = mt._tolerance
        delta = range * tolerance
        VALUES = (0.0,
                  28.0,
                  mt.lower_limit + (random() * 2 * delta - delta),
                  80.0,
                  mt.upper_limit + (random() * 2 * delta - delta),
                  356.0)
        for value, rate in zip(VALUES, RATINGS.values()):
            mt.value = value
            self.assertEqual(mt.rating(), rate)

    def test_str_return(self):
        pt = Analysis.objects.get(name='puzzotropina')
        self.assertIn('100', str(pt))
        self.assertNotEqual(str(pt)[-1], 'n')
        pt.value = None
        self.assertNotIn('100', str(pt))
        self.assertEqual(str(pt)[-1], 'n')



