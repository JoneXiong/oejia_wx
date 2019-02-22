# coding=utf-8
import datetime
import logging
from odoo import fields

_logger = logging.getLogger(__name__)


class EntryBase(object):

    def __init__(self):
        self.UUID_OPENID = {}
        self.OPENID_UUID = {}

    def get_uuid_from_openid(self, uid):
        uuid = None
        _key = '%s'%uid
        if _key in self.OPENID_UUID:
            _data = self.OPENID_UUID[_key]
            _now = fields.datetime.now()
            if _now - _data['last_time']<=  datetime.timedelta(seconds=10*60):
                uuid = _data['uuid']
                self.update_lt(uid)
        return uuid

    def create_uuid_for_openid(self, uid, uuid):
        _logger.info('>>> create_uuid_for_openid %s %s', uid, uuid)
        _key = '%s'%uid
        if _key not in self.OPENID_UUID:
            self.OPENID_UUID[_key] = {}
        self.OPENID_UUID[_key]['last_time'] = fields.datetime.now()
        self.OPENID_UUID[_key]['uuid'] = uuid
        self.UUID_OPENID[uuid] = uid

    def update_lt(self, uid):
        _key = '%s'%uid
        self.OPENID_UUID[_key]['last_time'] = fields.datetime.now()

    def delete_uuid(self, uuid):
        openid = self.UUID_OPENID.get(uuid,None)
        if openid:
            del self.UUID_OPENID[uuid]
            if openid in self.OPENID_UUID:
                del self.OPENID_UUID[openid]


    def get_openid_from_uuid(self, uuid):
        return self.UUID_OPENID.get(uuid,None)
