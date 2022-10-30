from datetime import date, time, datetime
from hashlib import sha224
from numpy import array, zeros


def cop_to_str(cop: array):
    s = list()
    for i in range(8):
        s.append(list_to_str(cop[i]))
    return ';'.join(map(str, s))


def str_to_cop(s: str):
    cop = zeros((8, 200))
    lines = s.split(';')
    for i, line in enumerate(lines):
        cop[i] = str_to_array(line)
    return cop


def str_to_array(lst: list):
    return array([float(x) for x in lst.split(',')])


def list_to_str(lst: list):
    return ','.join(map(str, lst))


def date_to_str(dt: date):
    return '-'.join(dt.isoformat().split('-')[-1::-1])


def datetime_to_str(dt: datetime):
    d, t = dt.date(), dt.time()
    d = date_to_str(d)
    return d + ' ' + t.isoformat()


def str_to_time(t: str):
    h, m, s = t.split(':')
    h, m = int(h), int(m)
    s = [int(x) for x in s.split('.')]
    return time(h, m, s[0], s[1])


def str_to_datetime(s: str):
    d, t = s.split()
    d = str_to_date(d)
    t = str_to_time(t)
    return datetime(d.year, d.month, d.day, t.hour, t.minute, t.second, t.microsecond)


def str_to_date(s: str):
    s = [int(x) for x in s.split('-')]
    return date(s[2], s[1], s[0])


def dict_to_strs(dct: dict):
    res = []
    for v in dct.values():
        res.append(list_to_str(v))
    return res


def strs_to_dict(ks: list, strs: list):
    res = {}
    for i, k in enumerate(ks):
        res[k] = str_to_array(strs[i])
    return res


def check_password(p1: str, p2: str):
    return p1 == sha224(p2.encode('utf-8')).hexdigest()


def crypt_password(p: str):
    return sha224(p.encode('utf-8')).hexdigest()
