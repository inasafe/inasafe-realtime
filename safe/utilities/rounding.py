# coding=utf-8

"""Rounding and number formatting.

Taken from InaSAFE version 4.
"""

from safe.utilities.i18n import locale

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def thousand_separator():
    """Return thousand separator according to the locale.

    :return: The thousand separator.
    :rtype: basestring
    """
    lang = locale()

    if lang in ['id']:
        return '.'

    elif lang in ['fr']:
        return ' '

    else:
        return ','


def add_separators(x):
    """Format integer with separator between thousands.

    :param x: A number to be formatted in a locale friendly way.
    :type x: int

    :returns: A locale friendly formatted string e.g. 1,000,0000.00
        representing the original x. If a ValueError exception occurs,
        x is simply returned.
    :rtype: basestring

    From http://
    stackoverflow.com/questions/5513615/add-thousands-separators-to-a-number

    Instead use this:
    http://docs.python.org/library/string.html#formatspec
    """
    try:
        s = '{0:,}'.format(x)
        # s = '{0:n}'.format(x)  # n means locale aware (read up on this)
    # see issue #526
    except ValueError:
        return x

    # Quick solution for the moment
    if locale() in ['id', 'fr']:
        # Replace commas with the correct thousand separator.
        s = s.replace(',', thousand_separator())
    return s


def fatalities_range(number):
    """A helper to return fatalities as a range of number.

    See https://github.com/inasafe/inasafe/issues/3666#issuecomment-283565297

    :param number: The exact number. Will be converted as a range.
    :type number: int, float

    :return: The range of the number.
    :rtype: str
    """
    range_format = '{min_range} - {max_range}'
    more_than_format = '> {min_range}'
    ranges = [
        [0, 100],
        [100, 1000],
        [1000, 10000],
        [10000, 100000],
        [100000, float('inf')]
    ]
    for r in ranges:
        min_range = r[0]
        max_range = r[1]

        if max_range == float('inf'):
            return more_than_format.format(
                min_range=add_separators(min_range))
        elif min_range <= number <= max_range:
            return range_format.format(
                min_range=add_separators(min_range),
                max_range=add_separators(max_range))
