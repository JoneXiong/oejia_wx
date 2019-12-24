import logging
_logger = logging.getLogger(__name__)

def multi(method):
    method._api = 'multi'
    return method

def model_cr(method):
    method._api = 'model_cr'
    return method

from odoo import api
api.multi = multi
api.model_cr = model_cr
try:
    from openerp import api
    api.multi = multi
    api.model_cr = model_cr
except:
    import traceback;traceback.print_exc()


from odoo import models
origin_write = models.BaseModel.write
def write(self, vals):
    _vals = {}
    for k,v in vals.items():
        if k in self._fields:
            _vals[k] = v
        else:
            _logger.warning('>>> odoo 13 hook: model %s has no field %s', self._name, k)
    #vals = { k:v for k,v in vals.items() if k in self._fields}
    return origin_write(self, _vals)
models.BaseModel.write = write

origin_create = models.BaseModel.create
@api.model_create_multi
def create(self, vals_list):
    _vals_list = []
    for vals in vals_list:
        _vals = {}
        for k,v in vals.items():
            if k in self._fields:
                _vals[k] = v
            else:
                _logger.warning('>>> odoo 13 hook: model %s has no field %s', self._name, k)
        #vals = { k:v for k,v in vals.items() if k in self._fields}
        _vals_list.append(_vals)
    return origin_create(self, _vals_list)
models.BaseModel.create = create
