import datetime
from django.core.exceptions import ValidationError
from django.db.models import CharField

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

    def __init__(self, year: int, month: int = None, day: int = None):
        if year < 0: raise ValueError
        self._year = year
        self._month = None
        self._day = None
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

    def __len__(self):
        return len(str(self))


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
