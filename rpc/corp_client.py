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

        super(CorpEntry, self).__init__()

    def get_uuid_from_uid(self, uid):
        uuid = None
        _key = '%s'%uid
        if _key in self.UID_UUID:
            _data = self.UID_UUID[_key]
            _now = datetime.datetime.now()
            if _now - _data['last_time']<=  datetime.timedelta(seconds=10*60):
                uuid = _data['uuid']
        return uuid

    def create_uuid_for_uid(self, uid, uuid, from_uid):
        _key = '%s'%uid
        if _key not in self.UID_UUID:
            self.UID_UUID[_key] = {}
        self.UID_UUID[_key]['from'] = from_uid
        self.UID_UUID[_key]['last_time'] = datetime.datetime.now()
        self.UID_UUID[_key]['uuid'] = uuid

    def update_uuid_lt(self, uid):
        _key = '%s'%uid
        self.UID_UUID[_key]['last_time'] = datetime.datetime.now()

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
                    _now = fields.datetime.now()
                    _d = _now - fields.Datetime.from_string(obj.last_uuid_time)
                    if _d <= datetime.timedelta(seconds=10*60):
                        self.create_uuid_for_openid(obj.userid, obj.last_uuid)
        except:
            env.cr.rollback()
            import traceback;traceback.print_exc()

        print('corp client init: %s %s'%(self.OPENID_UUID, self.UUID_OPENID))

def corpenv(env):
    return CorpEnvDict[env.cr.dbname]
