from enum import Enum


class Country(Enum):
    CHINA = 0
    INDIA = 1
    ITALY = 2
    US = 3


def get_country_name(country):
    if country == Country.US:
        return country.name
    else:
        return country.name.capitalize()
