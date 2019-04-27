# coding=utf-8
import os
import sys


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from .hook import OdooHook
sys.meta_path.append(OdooHook())


cur_dir = os.path.abspath(os.path.join( os.path.dirname(__file__) ) )
ext_path = os.path.join(cur_dir, 'ext_libs')
sys.path.append(ext_path)

from . import controllers
from . import models
