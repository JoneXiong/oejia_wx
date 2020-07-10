# coding=utf-8
import datetime
import logging
import os
import traceback
import time
import json

import odoo
from odoo import fields
from wechatpy.session import SessionStorage
from wechatpy.utils import to_text

_logger = logging.getLogger(__name__)


class EntryBase(object):

    def __init__(self):
        self.UUID_OPENID = {}
        self.OPENID_UUID = {}
        self.OPENID_LAST = {}

    def get_path(self, key):
        data_dir = odoo.tools.config['data_dir']
        cls_name = self.__class__.__name__
        return '%s/%s-%s/%s'%(data_dir, cls_name, key, self.dbname)

    def init_data(self, env):
        from diskcache import Index
        self.dbname = env.cr.dbname
        self.UUID_OPENID = Index(self.get_path('UUID_OPENID'))
        self.OPENID_UUID = Index(self.get_path('OPENID_UUID'))
        self.OPENID_LAST = Index(self.get_path('OPENID_LAST'))

    def update_index(self, index, key, data):
        _dict = index[key]
        _dict.update(data)
        index[key] = _dict

    def get_uuid_from_openid(self, uid, update=True):
        uuid = None
        record_uuid = None
        _key = '%s'%uid
        _logger.info('>>> get_uuid_from_openid %s', _key)
        if _key in self.OPENID_UUID:
            _data = self.OPENID_UUID[_key]
            _now = fields.datetime.now()
            if 'uuid' not in _data:
                return uuid, record_uuid
            record_uuid = _data['uuid']
            if _now - _data['last_time']<=  datetime.timedelta(seconds=10*60):
                uuid = _data['uuid']
                if update:
                    self.update_lt(uid)
        return uuid, record_uuid

    def create_uuid_for_openid(self, uid, uuid):
        _logger.info('>>> create_uuid_for_openid %s %s', uid, uuid)
        _key = '%s'%uid
        if _key not in self.OPENID_UUID:
            self.OPENID_UUID[_key] = {}
        self.update_index(self.OPENID_UUID, _key, {'last_time': fields.datetime.now(), 'uuid': uuid})
        self.UUID_OPENID[uuid] = uid

    def recover_uuid(self, uid, uuid, lt):
        _logger.info('>>> recover_uuid %s %s', uid, uuid)
        _key = '%s'%uid
        if _key not in self.OPENID_UUID:
            self.OPENID_UUID[_key] = {}
        self.update_index(self.OPENID_UUID, _key, {'last_time': lt, 'uuid': uuid})
        self.UUID_OPENID[uuid] = uid

    def update_lt(self, uid):
        _key = '%s'%uid
        self.update_index(self.OPENID_UUID, _key, {'last_time': fields.datetime.now()})

    def delete_uuid(self, uuid):
        openid = self.UUID_OPENID.get(uuid,None)
        if openid:
            del self.UUID_OPENID[uuid]
            if openid in self.OPENID_UUID:
                del self.OPENID_UUID[openid]


    def get_openid_from_uuid(self, uuid):
        return self.UUID_OPENID.get(uuid,None)

    def get_active_uuids(self):
        uuid_list = []
        for openid in self.OPENID_UUID.keys():
            uuid = self.get_uuid_from_openid(openid, update=False)
            if uuid:
                uuid_list.append(uuid)
        return uuid_list

    def gen_session(self):
        return SessionStorage(self.dbname)


class SessionStorage(SessionStorage):

    def __init__(self, dbname):
        self.file_dir = '%s/%s'%(odoo.tools.config['data_dir'], dbname)

    def get(self, key, default=None):
        try:
            with open('%s-%s'%(self.file_dir, key), 'r') as f:
                _dict = json.loads(to_text(f.read()))
                timestamp = time.time()
                expires_at = _dict.get('expires_at', 0)
                if expires_at==0 or expires_at - timestamp > 60:
                    return _dict['val']
        except:
            traceback.print_exc()
            return default

    def set(self, key, value, ttl=None):
        if value is None:
            return
        with open('%s-%s'%(self.file_dir, key), 'w') as f:
            value = json.dumps({'val': value, 'expires_at': ttl and int(time.time()) + ttl or 0})
            f.write(value)

    def delete(self, key):
        self.set(key, '')
