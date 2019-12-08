# -*- coding: utf-8 -*-


def embolden(s):
    return f'\002{s}\002'


def listtostr(iterable, conj="and"):
    lst = list(iterable)
    if len(lst) == 1:
        return lst[0]
    else:
        return ', '.join(lst[:-1]) + f' {conj} {lst[-1]}'
