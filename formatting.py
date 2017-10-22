# -*- coding: utf-8 -*-


def embolden(s):
    return '\002{}\002'.format(s)


def listtostr(lst, conj="and"):
    return ", ".join(lst[:-1]) + " " + conj + " " + lst[-1] if len(lst) > 1 else lst[0]
