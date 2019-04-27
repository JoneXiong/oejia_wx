# coding=utf-8

import pkg_resources
import re
import sys


import imp
import importlib
import inspect
import itertools
import logging
import os
import pkg_resources
import re
import sys
import time
import types
import unittest
import threading


from openerp.exceptions import ValidationError
from openerp import exceptions
exceptions.UserError = ValidationError


class AddonsHook(object):
    """ Makes modules accessible through openerp.addons.* and odoo.addons.* """

    def find_module(self, name, path=None):
        if name.startswith(('odoo.addons.',))\
                and name.count('.') == 2:
            return self

    def load_module(self, name):
        assert name not in sys.modules

        # get canonical names
        odoo_name = re.sub(r'^openerp.addons.(\w+)$', r'odoo.addons.\g<1>', name)
        openerp_name = re.sub(r'^odoo.addons.(\w+)$', r'openerp.addons.\g<1>', odoo_name)

        assert odoo_name not in sys.modules
        assert openerp_name not in sys.modules

        # get module name in addons paths
        _1, _2, addon_name = name.split('.')
        # load module
        f, path, (_suffix, _mode, type_) = imp.find_module(addon_name, ad_paths)
        if f: f.close()

        # TODO: fetch existing module from sys.modules if reloads permitted
        # create empty odoo.addons.* module, set name
        new_mod = types.ModuleType(odoo_name)
        new_mod.__loader__ = self

        # module top-level can only be a package
        assert type_ == imp.PKG_DIRECTORY, "Odoo addon top-level must be a package"
        modfile = opj(path, '__init__.py')
        new_mod.__file__ = modfile
        new_mod.__path__ = [path]
        new_mod.__package__ = odoo_name

        # both base and alias should be in sys.modules to handle recursive and
        # corecursive situations
        sys.modules[odoo_name] = sys.modules[openerp_name] = new_mod

        # execute source in context of module *after* putting everything in
        # sys.modules, so recursive import works
        execfile(modfile, new_mod.__dict__)

        # people import openerp.addons and expect openerp.addons.<module> to work
        setattr(odoo.addons, addon_name, new_mod)

        return sys.modules[name]
# need to register loader with setuptools as Jinja relies on it when using
# PackageLoader
#pkg_resources.register_loader_type(AddonsHook, pkg_resources.DefaultProvider)

class OdooHook(object):
    """ Makes odoo package also available as openerp """

    def find_module(self, name, path=None):
        # openerp.addons.<identifier> should already be matched by AddonsHook,
        # only framework and subdirectories of modules should match
        if re.match(r'^odoo\b', name):
            return self

    def load_module(self, name):
        assert name not in sys.modules

        canonical = re.sub(r'^odoo(.*)', r'openerp\g<1>', name)

        if canonical in sys.modules:
            mod = sys.modules[canonical]
        else:
            # probable failure: canonical execution calling old naming -> corecursion
            mod = importlib.import_module(canonical)

        # just set the original module at the new location. Don't proxy,
        # it breaks *-import (unless you can find how `from a import *` lists
        # what's supposed to be imported by `*`, and manage to override it)
        sys.modules[name] = mod

        return sys.modules[name]
