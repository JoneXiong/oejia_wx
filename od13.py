def multi(method):
    return method
from odoo import api
api.multi = multi
from openerp import api
api.multi = multi


from odoo import models
origin_write = models.Model.write
def write(self, vals):
    vals = [e for e in vals if e in self._fields]
    return origin_write(self, vals)
models.Model.write = write
