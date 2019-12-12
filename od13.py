import logging
_logger = logging.getLogger(__name__)

def nothing(method):
    return method
from odoo import api
api.multi = nothing
api.model_cr = nothing
try:
    from openerp import api
    api.multi = nothing
    api.model_cr = nothing
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
