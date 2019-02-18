from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django import utils

from patients.tools import ItalianPeriodDateField
from .managers import AnalysisManager

SEX_CHOICES = (('f', 'femmina'), ('m', 'maschio'))
RATINGS = {'zero': '0',
           'basso': 'b',
           'limite inferiore': 'li',
           'normale': 'n',
           'limite superiore': 'ls',
           'alto': 'a'}
RATING_CHOICES = tuple((k, v) for v, k in RATINGS.items())
RATING_CODES = tuple(RATINGS.keys())
EMPTY_ANALYSIS_DATA = {'value': None, 'rate': None, 'lower_limit': None,
                           'upper_limit': None, 'name': None, 'unit': None}

class Patient(models.Model): # TODO: make fields mandatory
    """Anagrafic data of a patient."""
    last_name = models.CharField(max_length=50, verbose_name='cognome')
    first_name = models.CharField(max_length=50, verbose_name='nome')
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, verbose_name='sesso')
    birth_date = models.DateField(verbose_name='data di nascita')
    birth_place = models.CharField(max_length=100, verbose_name='luogo di nascita')
    fiscal_code = models.CharField(max_length=16, blank=True, null=True,
                                   verbose_name='codice fiscale')
    address = models.CharField(max_length=200, blank=True, null=True,
                               verbose_name='indirizzo')

    def clean(self):
        self.last_name = self.last_name.lower()
        self.first_name = self.first_name.lower()
        if self.birth_place:
            self.birth_place = self.birth_place.lower()
        if self.fiscal_code:
            self.fiscal_code = self.fiscal_code.upper()

    def __str__(self):
        return f"{self.last_name} {self.first_name} - " \
            f"{self.sex} - {self.birth_date.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = 'paziente'
        verbose_name_plural = 'pazienti'


class ExemptionCodes(models.Model):
    """Chronic disease exemption code in Italian health system."""
    code = models.CharField(max_length=10, verbose_name='codice')
    name = models.CharField(max_length=200, verbose_name='nome')
    short_name = models.CharField(max_length=10, verbose_name='abbreviazione')

    def __str__(self):
        return f"{self.code} ({self.short_name})"

    class Meta:
        verbose_name = 'codice esenzione'
        verbose_name_plural = 'codici esenzione'


class Place(models.Model):
    municipality = models.CharField(verbose_name='comune', max_length=50)

    def __str__(self):
        return self.municipality

    class Meta:
        verbose_name = 'luogo'
        verbose_name_plural = 'luoghi'


class Exemption(models.Model):
    """Data of an exemption document."""
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True,
                                blank=True, verbose_name='paziente')
    exemption = models.ForeignKey(ExemptionCodes, on_delete=models.SET_NULL,
                                  null=True, verbose_name='esenzione')
    name = models.CharField(max_length=150, null=True, default=' ',
                            blank=True, verbose_name='nome paziente')
    birth_place = models.CharField(max_length=50, null=True, blank=True,
                                   verbose_name='luogo di nascita',
                                   default=None)
    birth_date = models.DateField(verbose_name='data di nascita', null=True,
                                  blank=True, default=None)
    signature_place = models.ForeignKey(Place, verbose_name='luogo',
                                        on_delete=models.CASCADE)
    signature_date = models.DateField(verbose_name='data',
                                      default=utils.timezone.now)

    def __str__(self):
        return f"{self.exemption} {self.name}"

    def clean(self):
        # if patient linked, populate fields with its data
        if self.patient:
            self.name = self.patient.last_name + ' ' + self.patient.first_name
            self.birth_date = self.patient.birth_date
            self.birth_place = self.patient.birth_place

    class Meta:
        verbose_name = 'esenzione'
        verbose_name_plural = 'esenzioni'


class Center(models.Model):
    """Wrap working center."""
    name = models.CharField(max_length=100, verbose_name='nome')
    municipality = models.CharField(verbose_name='comune', max_length=50)
    address = models.CharField(max_length=200, blank=True, null=True,
                               verbose_name='indirizzo')
    stamp = models.ImageField(verbose_name='timbro', blank=True, null=True)

    def __str__(self):
        return self.name.title()

    class Meta:
        verbose_name = 'centro'
        verbose_name_plural = 'centri'


class ClinicalElement(models.Model):
    """Abstract base class for disorders, analyses and exams."""
    date = ItalianPeriodDateField(verbose_name='data', default='01/01/2000')
    name = models.CharField(verbose_name='nome', max_length=250)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE,
                                verbose_name='paziente')

    class Meta:
        abstract = True


class AnalysisName(models.Model):

    name = models.CharField(verbose_name='nome', max_length=100)
    short_name = models.CharField(verbose_name='abbreviazione', max_length=25)

    def __str__(self):
        return f"{self.name} ({self.short_name})"

    class Meta:
        verbose_name = 'tipo analisi'
        verbose_name_plural = "tipi analisi"


class Analysis(ClinicalElement):
    """Blood, urine etc. analyses."""
    name = models.ForeignKey(AnalysisName, verbose_name='nome',
                             on_delete=models.CASCADE)
    value = models.FloatField(blank=True, null=True, verbose_name='valore',
                              validators=[MinValueValidator(limit_value=0),])
    rate = models.CharField(max_length=2, choices=RATING_CHOICES, blank=True,
                            verbose_name='valutazione', null=True)
    lower_limit = models.FloatField(blank=True, null=True,
                                    verbose_name='limite inferiore')
    upper_limit = models.FloatField(blank=True, null=True,
                                    verbose_name='limite superiore')
    unit = models.CharField(max_length=10, verbose_name='unità di misura',
                            blank=True, null=True)
    objects = AnalysisManager()
    _tolerance = 0.05

    def rating(self): # TODO: ugly function
        """If not user rated, return the rating of this Analysis."""
        if self.rate: return self.rate
        if not self.lower_limit: return None
        if not self.upper_limit: return None

        range = self.upper_limit - self.lower_limit
        delta = range * self._tolerance

        if self.value == 0:
            return RATINGS['zero']
        elif self.value < self.lower_limit - delta:
            return RATINGS['basso']
        elif self.lower_limit - delta <= self.value <= self.lower_limit + delta:
            return RATINGS['limite inferiore']
        elif self.lower_limit + delta < self.value < self.upper_limit - delta:
            return RATINGS['normale']
        elif self.upper_limit - delta <= self.value <= self.upper_limit + delta:
            return RATINGS['limite superiore']
        elif self.value > self.upper_limit + delta:
            return RATINGS['alto']

    def clean(self):
        """Value or rate need to be set."""
        if self.value or self.rate:
            return
        raise ValidationError('Either value or rate must be set.')

    def __str__(self):

        form = f"{str(self.date)} {self.name.short_name} " # TODO: return better date
        if self.value:
            form = form + str(self.value)
            if self.unit:
                form = ' ' + form + ' ' + self.unit
            return form
        return form + '(' + self.rating() + ')'

    class Meta:
        verbose_name = 'analisi'
        verbose_name_plural = 'analisi'


class BMD(ClinicalElement):
    name = models.CharField(max_length=3, default='MOC', verbose_name='moc')
    ls_t = models.FloatField(verbose_name="lombosacrale T-score", blank=True, null=True)
    ls_z = models.FloatField(verbose_name="lombosacrale Z-score", blank=True, null=True)
    ls_bmd = models.FloatField(verbose_name="lombosacrale BMD", blank=True, null=True)
    fn_t = models.FloatField(verbose_name="femoral neck T-score", blank=True, null=True)
    fn_z = models.FloatField(verbose_name="femoral neck Z-score", blank=True, null=True)
    fn_bmd = models.FloatField(verbose_name="femoral neck BMD", blank=True, null=True)
    ft_t = models.FloatField(verbose_name="femorale totale T-score", blank=True, null=True)
    ft_z = models.FloatField(verbose_name="femorale totale Z-score", blank=True, null=True)
    ft_bmd = models.FloatField(verbose_name="femorale totale BMD", blank=True, null=True)

    def __str__(self):
        return f"MOC {str(self.date)}"

    class Meta:
        verbose_name = 'MOC'
        verbose_name_plural = 'MOC'


# class TestModel(models.Model):
#     date = ItalianPeriodDateField(verbose_name='data')
#
#     def __str__(self):
#         return str(self.date)


