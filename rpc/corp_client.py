# coding=utf-8
import logging
import datetime

from wechatpy.enterprise import WeChatClient
from odoo import fields
from .base import EntryBase

_logger = logging.getLogger(__name__)


CorpEnvDict = {}

class CorpEntry(EntryBase):

    def __init__(self):

        self.crypto_handle = None

        # 用于agent应用API交互的client
        self.client = None

        # 用于通讯录API交互的client
        self.txl_client = None

        # 当前Agent
        self.current_agent = None

        # 微信用户对应的Odoo用户ID缓存
        self.OPENID_UID = {}

        # 企业微信用户(绑定了Odoo用户)和Odoo的会话缓存(由Odoo用户发起, key 为 db-uid)
        self.UID_UUID = {}
        self.UID_CURRENT_SID = {}

        super(CorpEntry, self).__init__()

    def _get_cur_key(self, uid):
        cur_sid = self.UID_CURRENT_SID[str(uid)]
        return '%s@%s'%(uid, cur_sid)

    def get_uuid_from_uid(self, uid):
        uuid = None
        _key = self._get_cur_key(uid)
        if _key in self.UID_UUID:
            _data = self.UID_UUID[_key]
            _now = datetime.datetime.now()
            if _now - _data['last_time']<=  datetime.timedelta(seconds=10*60):
                uuid = _data['uuid']
        return uuid

    def create_uuid_for_uid(self, uid, uuid, from_uid):
        sid = self.gen_new_sid(uid)
        _key = '%s@%s'%(uid, sid)
        if _key not in self.UID_UUID:
            self.UID_UUID[_key] = {}
        self.UID_UUID[_key]['from'] = from_uid
        self.UID_UUID[_key]['last_time'] = datetime.datetime.now()
        self.UID_UUID[_key]['uuid'] = uuid
        return sid

    def update_uuid_lt(self, uid):
        _key = self._get_cur_key(uid)
        self.UID_UUID[_key]['last_time'] = datetime.datetime.now()

    def set_uid_cur_sid(self, uid, sid):
        sid_list = self.get_active_sid_list(uid)
        if sid in sid_list:
            self.UID_CURRENT_SID[str(uid)] = sid
            return 0
        else:
            return 1

    def update_sid_lt(self, uid, sid):
        '''
        更新指定会话lt
        '''
        _key = '%s@%s'%(uid, sid)
        self.UID_UUID[_key]['last_time'] = datetime.datetime.now()

    def get_uuid_from_key(self, key):
        '''
        获取指定会话的uuid
        '''
        uuid = None
        _key = '%s'%key
        if _key in self.UID_UUID:
            _data = self.UID_UUID[_key]
            _now = datetime.datetime.now()
            if _now - _data['last_time']<=  datetime.timedelta(seconds=10*60):
                uuid = _data['uuid']
        return uuid

    def get_active_sid_list(self, uid):
        '''
        获取当前活跃的会话 sid 列表
        '''
        sid_list = []
        for key in self.UID_UUID.keys():
            uuid = self.get_uuid_from_key(key)
            if uuid:
                userid, sid = key.split('@')
                if str(userid)==str(uid):
                    sid_list.append(int(sid))
        return sid_list

    def get_active_sid_map(self, uid):
        '''
        获取当前活跃 dict { uuid : sid }
        '''
        uuid_sid_map = {}
        for key in self.UID_UUID.keys():
            uuid = self.get_uuid_from_key(key)
            if uuid:
                userid, sid = key.split('@')
                if str(userid)==str(uid):
                    uuid_sid_map[uuid] = int(sid)
        return uuid_sid_map

    def get_sid_from_uuid(self, uid, uuid):
        '''
        获取sid, 通过 uuid
        '''
        sid_map = self.get_active_sid_map(uid)
        return sid_map.get(uuid, None)

    def gen_new_sid(self, uid):
        '''
        生成新的会话 sid
        '''
        sid_list = self.get_active_sid_list(uid)
        if sid_list:
            _max = max(sid_list)
            for i in range(1,_max+2):
                if i not in sid_list:
                    return i
        else:
            self.UID_CURRENT_SID[str(uid)] = 1
            return 1

    def init_client(self, appid, secret):
        self.client = WeChatClient(appid, secret)
        return self.client

    def init_txl_client(self, appid, secret):
        self.txl_client = WeChatClient(appid, secret)
        return self.txl_client

    def chat_send(self, uuid, msg):
        openid = self.get_openid_from_uuid(uuid)
        if openid:
            self.client.message.send_text(self.current_agent, openid, msg)

    def init(self, env):
        global CorpEnvDict
        CorpEnvDict[env.cr.dbname] = self

        Param = env['ir.config_parameter'].sudo()

        Corp_Token = Param.get_param('Corp_Token') or ''
        Corp_AESKey = Param.get_param('Corp_AESKey') or ''

        Corp_Id = Param.get_param('Corp_Id') or ''       # 企业号
        Corp_Secret = Param.get_param('Corp_Secret') or ''
        Corp_Agent = Param.get_param('Corp_Agent') or 0
        Corp_Agent_Secret = Param.get_param('Corp_Agent_Secret') or ''

        from wechatpy.enterprise.crypto import WeChatCrypto
        _logger.info('Create crypto: %s %s %s'%(Corp_Token, Corp_AESKey, Corp_Id))
        try:
            self.crypto_handle = WeChatCrypto(Corp_Token, Corp_AESKey, Corp_Id)
        except:
            _logger.error(u'初始化企业微信客户端实例失败，请在微信对接配置中填写好相关信息！')
        self.init_client(Corp_Id, Corp_Agent_Secret)
        self.init_txl_client(Corp_Id, Corp_Secret)
        self.current_agent = Corp_Agent

        try:
            users = env['wx.corpuser'].sudo().search([('last_uuid','!=',None)])
            for obj in users:
                if obj.last_uuid_time:
                    self.recover_uuid(obj.userid, obj.last_uuid, fields.Datetime.from_string(obj.last_uuid_time))
        except:
            env.cr.rollback()
            import traceback;traceback.print_exc()

        print('corp client init: %s %s'%(self.OPENID_UUID, self.UUID_OPENID))

def corpenv(env):
    return CorpEnvDict[env.cr.dbname]
