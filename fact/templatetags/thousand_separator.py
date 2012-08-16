#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import template

register = template.Library()

def thousand_separator(value, arg):
    """ Replace in value arg by space """
    return value.replace(arg, ' ')

register.filter('thousand_separator', thousand_separator)
