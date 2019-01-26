from django.db import models
from django import utils

SEX_CHOICES = (('f', 'femmina'), ('m', 'maschio'))

class Patient(models.Model): # TODO: make fields mandatory
    """Anagrafic data of a patient."""
    last_name = models.CharField(max_length=50, verbose_name='cognome')
    first_name = models.CharField(max_length=50, verbose_name='nome')
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, verbose_name='sesso')
    birth_date = models.DateField(verbose_name='data di nascita')
    birth_place = models.CharField(max_length=100, blank=True, null=True,
                                   verbose_name='luogo di nascita')
    fiscal_code = models.CharField(max_length=16, blank=True, null=True,
                                   verbose_name='codice fiscale')
    address = models.CharField(max_length=200, blank=True, null=True,
                               verbose_name='indirizzo')

    def save(self, *args, **kwargs):
        self.last_name = self.last_name.lower()
        self.first_name = self.first_name.lower()
        if self.birth_place:
            self.birth_place = self.birth_place.lower()
        if self.fiscal_code:
            self.fiscal_code = self.fiscal_code.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} {} - {} - {}'.format(self.last_name, self.first_name,
                                        self.sex, self.birth_date).title()
    # TODO: make birth date right format

    class Meta:
        verbose_name = 'paziente'
        verbose_name_plural = 'pazienti'


class ExemptionCodes(models.Model):
    """Chronic disease exemption code in Italian health system."""
    code = models.CharField(max_length=10, verbose_name='codice')
    name = models.CharField(max_length=200, verbose_name='nome')
    short_name = models.CharField(max_length=10, verbose_name='abbreviazione')

    def __str__(self):
        return self.code + ' (' + self.short_name + ')'

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
        return str(self.exemption) + ' ' + self.name

    def save(self, *args, **kwargs):
        # if patient linked, populate fields with its data
        if self.patient:
            self.name = self.patient.last_name + ' ' + self.patient.first_name
            self.birth_date = self.patient.birth_date
            self.birth_place = self.patient.birth_place
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'esenzione'
        verbose_name_plural = 'esenzioni'


class ClinicalElement(models.Model):
    """Abstract base class for disorders, analyses and exams."""
    date = models.DateField(verbose_name='data')
    name = models.CharField(verbose_name='nome', max_length=250)
    content = models.CharField(verbose_name='valore', max_length=1000)

    class Meta:
        abstract = True


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


