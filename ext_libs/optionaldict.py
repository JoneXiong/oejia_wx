# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import sys


__version__ = '0.1.1'
__author__ = 'messense'
__all__ = ['optionaldict', 'OptionalDict']

PY3 = sys.version_info[0] == 3
if PY3:
    def _iteritems(d, **kwargs):
        return iter(d.items(**kwargs))
else:
    def _iteritems(d, **kwargs):
        return iter(d.iteritems(**kwargs))


class OptionalDict(dict):
    """A dictionary only store non none values"""
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        if value is None:
            return
        return dict_setitem(self, key, value)

    def update(self, *args, **kwargs):
        for k, v in _iteritems(dict(*args, **kwargs)):
            self[k] = v

    def setdefault(self, k, d=None, dict_setdefault=dict.setdefault):
        if d is None:
            return
        return dict_setdefault(self, k, d)


optionaldict = OptionalDict
