#!/usr/bin/env python
# encoding=utf-8

''' Converts numbers into french letters.

    * very basic version
    * does not support plurals (deux millions)
    * does not support floats '''


def cel(num):

    units_map = [u"zéro", u"un", u"deux", u"trois", u"quatre", u"cinq", \
                u"six", u"sept", u"huit", u"neuf", u"dix", u"onze", u"douze", \
                u"treize", u"quatorze", u"qunize", u"seize"]

    tens_map = {20: u"vingt", 30: u"trente", 40: u"quarante", \
                50: u"cinquante", 60: u"soixante", 70: u"soixante-dix", \
                80: u"quatre-vingt", 90: u"quatre-vingt-dix"}

    num = str(num).strip().replace(' ', '').replace(',', '.')

    try:
        num = int(num)
    except ValueError:
        num = float(num)
        return str(num)

    if num < 0:
        return u"moins %s" % cel(-num)

    if num < 17:
        return units_map[num]

    if num < 20:
        return u"dix-%s" % cel(num - 10)

    if num < 100:
        if num % 10 == 0:
            return tens_map[num]

        if num < 70:
            if num % 10 == 1:
                return u"%s-et-%s" % (cel(num - num % 10), cel(num % 10))
            return u"%s %s" % (cel(num - num % 10), cel(num % 10))
        elif num < 80:
            if num % 10 == 1:
                return u"%s-et-%s" % (cel(num - num % 60), cel(num % 20))
            return u"%s %s" % (cel(60), cel(num % 20))

        return u"%s %s" % (cel(80), cel(num % 20))

    if num == 100:
        return u"cent"

    if num < 200:
        return u"%s %s" % (cel(100), cel(num % 100))

    if num < 1000:
        if num % 100 != 0:
            end = u" %s" % cel(num % 100)
        else:
            end = u""
        return u"%s %s%s" % (cel(int(num / 100)), cel(100), end)

    if num == 1000:
        return u"mille"

    if num < 2000:
        return u"%s %s " % (cel(1000), cel(num % 1000))

    if num < 1000000:
        if num % 1000 != 0:
            end = u" %s" % cel(num % 1000)
        else:
            end = u""
        return u"%s %s%s" % (cel(int(num / 1000)), cel(1000), end)

    if num == 1000000:
        return u"million"

    if num < 2000000:
        return u"%s %s " % (cel(1000000), cel(num % 1000000))

    if num < 1000000000:
        if num % 1000000 != 0:
            end = u" %s" % cel(num % 1000000)
        else:
            end = u""
        return u"%s %s%s" % (cel(int(num / 1000000)), cel(1000000), end)

    return str(num)
