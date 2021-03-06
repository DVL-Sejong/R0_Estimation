from R0_Estimation.util import get_date_format
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum

import hashlib


class Country(Enum):
    INDIA = 0
    ITALY = 1
    US = 2


class InfoType(Enum):
    PRE = 0
    TEST = 1
    DEBUG = 2


@dataclass
class PreprocessInfo:
    country: Country = None
    _country: Country = field(init=False, repr=False)
    start: datetime = None
    _start: datetime = field(init=False, repr=False)
    end: datetime = None
    _end: datetime = field(init=False, repr=False)
    increase: bool = None
    _increase: bool = field(default=True)
    daily: bool = None
    _daily: bool = field(default=False)
    remove_zero: bool = None
    _remove_zero: bool = field(default=False)
    smoothing: bool = None
    _smoothing: bool = field(default=False)
    window: int = None
    _window: int = field(default=False)
    divide: bool = None
    _divide: bool = field(default=True)
    info_type: InfoType = None
    _info_type: InfoType = field(default=True)

    def __init__(self, country, start, end,
                 increase: bool, daily: bool, remove_zero: bool,
                 smoothing: bool, window: int, divide: bool, info_type: InfoType):
        self.country = country
        self.start = start
        self.end = end
        self.increase = increase
        self.daily = daily
        self.remove_zero = remove_zero
        self.smoothing = smoothing
        self.window = window
        self.divide = divide
        self.info_type = info_type

        self.check_valid()

    def __repr__(self):
        representation = f'PreprocessInfo(country: {self._country.name}, start: {self._start}, end: {self._end}, '
        representation += f'increase: {self._increase}, daily: {self._daily}, remove_zero: {self._remove_zero}, '
        representation += f'smoothing: {self._smoothing}, window: {self._window}, divide: {self._divide})'
        return representation

    @property
    def country(self) -> Country:
        return self._country

    @country.setter
    def country(self, country: Country):
        self._country = country

    @property
    def start(self):
        if hasattr(self, '_start'):
            return self._start
        else:
            return None

    def start_tostring(self, format: str = '%y%m%d'):
        if hasattr(self, '_start'):
            return self._start.strftime(format)
        else:
            return ''

    @start.setter
    def start(self, start):
        if start is None:
            self._start = datetime.now().date()

        if isinstance(start, str):
            format = get_date_format(start)
            self._start = datetime.strptime(start, format).date()
        elif isinstance(start, datetime):
            self._start = start.date()
        elif isinstance(start, date):
            self._start = start

    @property
    def end(self):
        if hasattr(self, '_end'):
            return self._end
        else:
            return None

    def end_tostring(self, format: str = '%y%m%d'):
        if hasattr(self, '_end'):
            return self._end.strftime(format)
        else:
            return ''

    @end.setter
    def end(self, end):
        if end is None:
            self._end = datetime.now().date()

        if isinstance(end, str):
            format = get_date_format(end)
            self._end = datetime.strptime(end, format).date()
        elif isinstance(end, datetime):
            self._end = end.date()
        elif isinstance(end, date):
            self._end = end

    @property
    def increase(self) -> bool:
        return self._increase

    @increase.setter
    def increase(self, increase: bool):
        self._increase = increase

    @property
    def daily(self) -> bool:
        return self._daily

    @daily.setter
    def daily(self, daily: bool):
        self._daily = daily

    @property
    def remove_zero(self) -> bool:
        return self._remove_zero

    @remove_zero.setter
    def remove_zero(self, remove_zero: bool):
        self._remove_zero = remove_zero

    @property
    def smoothing(self) -> bool:
        return self._smoothing

    @smoothing.setter
    def smoothing(self, smoothing: bool):
        self._smoothing = smoothing

    @property
    def window(self) -> int:
       return self._window

    @window.setter
    def window(self, window: int):
        if self._smoothing is False:
            self._window = 0
        else:
            self._window = window

    @property
    def divide(self) -> bool:
        return self._divide

    @divide.setter
    def divide(self, divide: bool):
        self._divide = divide

    @property
    def info_type(self) -> InfoType:
        return self._info_type

    @info_type.setter
    def info_type(self, info_type: InfoType):
        self._info_type = info_type

    def get_hash(self):
        hash_key = hashlib.sha1(self.__repr__().encode()).hexdigest()[:6]
        return hash_key

    def check_valid(self):
        if self.info_type is InfoType.TEST:
            if self.increase is True:
                raise ValueError(f'increase cannot be True for test number dataset!')
            if self.divide is True:
                raise ValueError(f'divide cannot be True for test number dataset!')


def get_country_name(country):
    if country == Country.US:
        return country.name
    else:
        return country.name.capitalize()
