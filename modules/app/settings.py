"""Settings for app."""

from enum import Enum


class Currencies(Enum):
    """
    Enum for currencies.
    """

    EUR = '€'
    USD = '$'


class Metrics(Enum):
    """
    Enum for metrics.
    """

    OPEN_PRICE = 'open_price'
    CLOSE_PRICE = 'close_price'
    VOLUME = 'volume'
