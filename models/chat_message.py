# coding=utf-8

import logging
import datetime

from openerp.osv import osv
from openerp.http import request
from ..controllers import client
from openerp import models, api

_logger = logging.getLogger(__name__)
