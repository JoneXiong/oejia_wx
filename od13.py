import logging
_logger = logging.getLogger(__name__)

def multi(method):
    return method
from odoo import api
api.multi = multi
from openerp import api
api.multi = multi


from odoo import models
origin_write = models.Model.write
def write(self, vals):
    _vals = {}
    for k,v in vals.items():
        if k in self._fields:
            _vals[k] = v
        else:
            _logger.warning('>>> odoo 13 hook: model %s has no field %s', self._name, k)
    #vals = { k:v for k,v in vals.items() if k in self._fields}
    return origin_write(self, _vals)
models.Model.write = write
