import datetime
from django.core.exceptions import ValidationError
from django.db.models import CharField
from django.http import HttpResponse
from django.views.generic.base import View
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph

EMPTY_ANALYSIS_DATA = {'value': None, 'rate': None, 'lower_limit': None,
                           'upper_limit': None, 'name': None, 'unit': None}


class TextToAnalysisTranslator: # TODO: ugly class!

    def text_to_analysis(self, text: str) -> tuple:
        # clean the string
        text = self.clean_text(text)
        # separate date an the analyses (rest of the string)
        date, analyses = self.separate_date_and_analyses(text)
        # separate the analysis tokens
        analysis_tokens = self.separate_analyses(analyses)
        # get analyses data
        analyses_data = self.extract_analysis_data(analysis_tokens)
        return date, analyses_data

    def clean_text(self, text: str) -> str:
        text = text.strip(' .')
        text = text.lower()
        return text

    def separate_date_and_analyses(self, text) -> (datetime.date, str):
        """Extract date from the start of the analyses string."""
        if text.startswith('- '):
            text = text.lstrip('- ')
        date_token, rest_of_the_string = text.split(' ', maxsplit=1)
        return date_token, rest_of_the_string

    def separate_analyses(self, text: str) -> list:
        analyses_tokens = text.split(',')
        analyses_tokens = [self.clean_text(a) for a in analyses_tokens]
        return analyses_tokens

    def extract_analysis_data(self, analysis_tokens: list) -> dict:
        analysis_data = []
        for token in analysis_tokens:
            analyte, content = token.split(' ', maxsplit=1)
            data = self.extract_data(content)
            data['name'] = analyte
            analysis_data.append(data)
        return analysis_data

    def extract_data(self, text: str) -> dict: # TODO: ugly function!
        tokens = text.split()
        content = dict(EMPTY_ANALYSIS_DATA)
        # control the first token to find value or rating
        if self.is_value(tokens[0]):
            content['value'] = float(tokens[0])
        else:
            content['rate'] = tokens[0] # TODO: check is a real rate
        # control the second token to find units
        if len(tokens) > 1:
            if self.is_range(tokens[1]):
                low, high = self.process_range(tokens[1])
                content['lower_limit'] = low
                content['upper_limit'] = high
            else:
                content['unit'] = tokens[1]
        # control the third token to find range
        if len(tokens) > 2:
            if self.is_range(tokens[2]):
                low, high = self.process_range(tokens[2])
                content['lower_limit'] = low
                content['upper_limit'] = high
        return content

    def is_value(self, token: str):
        try:
            value = float(token)
        except ValueError:
            return False
        return True

    def is_range(self, token: str) -> bool:
        # if it starts and ends with ( ) it's a range.
        return token.startswith('(') and token.endswith(')')

    def process_range(self, text: str):
        text = text.strip('()')
        if text.startswith('<'):
            low = None
            high = float(text.strip('<'))
        elif text.startswith('>'):
            low = float(text.strip('>'))
            high = None
        else:
            low, high = text.split('-')
            low = float(low)
            high = float(high)
        return low, high


class ItalianPeriodDate:

    MONTH_DURATION = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    LIMIT_FOR_2K = 70 # 72 --> 1972; 55 --> 2055

    def __init__(self, year: int, month: int = None, day: int = None):
        if year < 0: raise ValueError("year must be positive.")
        digits = len(str(year))
        if digits != 2 and digits != 4:
            raise ValueError("year must be 2 or 4 digits.")
        if year < 100:
            if year < self.LIMIT_FOR_2K:
                year = 2000 + year
            else:
                year = 1900 + year
        self._year = year
        self._month = None
        self._day = None
        if month is None and bool(day) is True:
            raise ValueError("Cannot set day without month.")
        if month:
            if month < 1 or month > 12:
                raise ValueError("month number out of range.")
            self._month = month
            if day:
                if day < 1 or day > self.MONTH_DURATION[self._month - 1]:
                    raise ValueError("day number out of range.")
                self._day = day

    @classmethod
    def fromstring(cls, time: str):
        """time: d/m/yy or d/m/yyyy or m/yy or m/yyyy or yyyy."""
        day = None
        month = None
        tokens = time.split('/')
        tokens.reverse()
        tokens_number = len(tokens)
        if tokens_number >= 1:
            year = int(tokens[0])
        if tokens_number > 1:
            month = int(tokens[1])
        if tokens_number > 2:
            day = int(tokens[2])
        return cls(year, month, day)

    def __str__(self):
        if self._day:
            day = str(self._day) + '/'
        else:
            day = ''
        if self._month:
            month = str(self._month) + '/'
        else:
            month = ''
        return f"{day}{month}{self._year}"

    def __eq__(self, other: 'ItalianPeriodDate') -> bool:
        return self._day == other._day \
           and self._month == other._month \
           and self._year == other._year

    def __ne__(self, other: 'ItalianPeriodDate') -> bool:
        return not self == other

    def __lt__(self, other: 'ItalianPeriodDate') -> bool:
        """'<' operator between two ItalianPeriodDate objects.

        28/11/1971 < 29/11/1971 < 12/1971 < 1972 is True, but
        28/11/1971 !< 11/1971  !< 1971  !!!
        """
        if self._year < other._year:
            return True
        if self._year == other._year:
            if self._month == other._month:
                if self._day is None or other._day is None:
                    raise TypeError("'<' not supported between 'YYYY/MM' and"
                                    " YYYY/MM/DD dates")
                if self._day < other._day:
                    return True
            if self._month is None or other._month is None:
                raise TypeError("'<' not supported between 'YYYY' and"
                                " YYYY/MM dates")
            if self._month < other._month:
                return True
        return False

    def __le__(self, other: 'ItalianPeriodDate') -> bool:
        return self == other or self < other

    def __gt__(self, other: 'ItalianPeriodDate') -> bool:
        """'>' operator between two ItalianPeriodDate objects.

        1971 > 12/1971 > 29/11/1971 > 28/11/1971 is True, but
        28/11/1971 !> 11/1971  !> 1971  !!!
        """
        if self._year > other._year:
            return True
        if self._year == other._year:
            if self._month == other._month:
                if self._day is None or other._day is None:
                    raise TypeError("'>' not supported between 'YYYY/MM' and"
                                    " YYYY/MM/DD dates")
                if self._day > other._day:
                    return True
            if self._month is None or other._month is None:
                raise TypeError("'>' not not supported between 'YYYY' and"
                                " YYYY/MM dates")
            if self._month > other._month:
                return True

        return False

    def __ge__(self, other: 'ItalianPeriodDate') -> bool:
        return self == other or self > other

    def __matmul__(self, other: 'ItalianPeriodDate') -> bool:
        """self @ other is True if self is closer to other.

        28/11/1971 @ 28/11/1971 is True (and also subdates)
        28/11/1971 @ 11/1971 is True
        11/1971 @ 1971 is True
        28/11/1971 @ 1971 is True
        """
        # check year inequality
        if self._year != other._year:
            return False # no matter what months and day are
        # here years are equal
        # check months equality
        if self._month == other._month:
            # here months are identical
            # check if they're both None
            if self._month is None and other._month is None:
                # here months are None
                # days must be both None (by definition in ItalianPeriodDate)
                return True
            else: # here months are numeric equal
                # check if days are equal
                if self._day == other._day:
                    # here days are identical numerically or None
                    # check if one or both is None
                    return True
                else: # here days are different
                    # check if one is None
                    if self._day is None or other._day is None:
                        # here one day is none
                        return True
                    else: # here days are numerically different
                        return False
        else: # here months are different
            # check if one is None
            if self._month is None or other._month is None:
                # here one month is None
                return True
            else: # here month are numerically different
                return False


class ItalianPeriodDateField(CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        # super().from_db_value(value, expression, connection)
        if value is None:
            return value
        try:
            return ItalianPeriodDate.fromstring(value)
        except ValueError:
            raise ValidationError('valore non valido')

    def to_python(self, value):
        if isinstance(value, ItalianPeriodDate):
            return value
        if value is None:
            return value
        try:
            return ItalianPeriodDate.fromstring(value)
        except ValueError:
            raise ValueError('valore non valido')

    def get_prep_value(self, value):
        return str(value)


class PDFGeneratorView(View):

    DEFAULT_PDF_FILE_NAME = 'doc'

    def get(self, request, *args, **kwargs):
        return self.render_to_response()

    def render_to_response(self):
        response = HttpResponse(content_type='application/pdf')
        response = self.make_pdf(response)
        response = self.make_pdf_file_name(response)
        return response

    def make_pdf(self, response: HttpResponse) -> HttpResponse:
        document = self.make_document(response)
        story = self.make_story()
        document.build(story)
        return response # TODO: add title of the pdf document

    def make_pdf_file_name(self, response: HttpResponse) -> HttpResponse:
        response['Content-Disposition'] = \
            f'attachment; filename="prova{self.DEFAULT_PDF_FILE_NAME}.pdf"'

    def make_document(self, response: HttpResponse) -> SimpleDocTemplate:
        return SimpleDocTemplate(response, pageSize=A4)

    def make_story(self) -> list:
        normal = ParagraphStyle(name='normal', fontName='Helvetica', fontSize=12)
        story = []
        story.append(Paragraph("Ciao", normal))
        return story
