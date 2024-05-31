from datetime import timedelta, datetime, date
from typing import Optional
import re

BOOL_MAP = {
    'true': True,
    't': True,
    '1': True,
    1: True,
    'false': False,
    'f': False,
    '0': False,
    0: False
}


def try_parse_date(d: str) -> date | None:
    '''Acceptable date formats

    '2006-10-25',      '25-10-2006',
    '25.10.2006',      '25/10/2006',
    '25 Oct 2006',     '25 10 2006',
    '2006/10/25',      '25 October 2006',
    'October 25 2006', '10-25-2006',
    '10/25/2006',      'Oct 25 2006',
    '2006 Oct 25',     '15-01-23',
    '15/01/23',        '10.25.2006',
    '''

    if isinstance(d, date):
        return d
    elif isinstance(d, datetime):
        return d.date()

    formats = (
        '%Y-%m-%d', '%d-%m-%Y',
        '%d.%m.%Y', '%d/%m/%Y',
        '%d %b %Y', '%d %m %Y',
        '%Y/%m/%d', '%d %B %Y',
        '%B %d %Y', '%m-%d-%Y',
        '%m/%d/%Y', '%b %d %Y',
        '%Y %b %d', '%d-%m-%y',
        '%d/%m/%y', '%m.%d.%Y',
    )
    for f in formats:
        try:
            return datetime.strptime(d, f).date()
        except:
            pass
    return None


def try_parse_bool(value: str | int) -> bool:
    try:
        if isinstance(value, str):
            value = value.lower()
        return BOOL_MAP[value]
    except KeyError as e:
        return False


def normalize_phone(phone: str) -> Optional[str]:
    if not phone:
        return None
    phone = re.sub(r'(\(|\)|-|\s|\+)', '', phone)
    phone = phone.lstrip('0')
    return phone


def format_offset(off):
    s = ''
    if off is not None:
        if off.days < 0:
            sign = "-"
            off = -off
        else:
            sign = "+"
        hh, mm = divmod(off, timedelta(hours=1))
        mm, ss = divmod(mm, timedelta(minutes=1))
        s += "%s%02d:%02d" % (sign, hh, mm)
        if ss or ss.microseconds:
            s += ":%02d" % ss.seconds

            if ss.microseconds:
                s += '.%06d' % ss.microseconds
    return s
