# coding=utf-8
import logging
import datetime

from wechatpy.enterprise import WeChatClient
from odoo import fields
from openerp.exceptions import ValidationError, UserError

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


    def init_client(self, appid, secret):
        self.client = WeChatClient(appid, secret, session=self.gen_session())
        return self.client

    def init_txl_client(self, appid, secret):
        self.txl_client = WeChatClient(appid, secret, session=self.gen_session())
        return self.txl_client

    def chat_send(self, uuid, msg):
        openid = self.get_openid_from_uuid(uuid)
        if openid:
            self.client.message.send_text(self.current_agent, openid, msg)

    def init(self, env, from_ui=False):
        self.init_data(env)
        global CorpEnvDict
        CorpEnvDict[env.cr.dbname] = self

        config = env['wx.corp.config'].sudo().get_cur()
        Corp_Token = config.Corp_Token
        Corp_AESKey = config.Corp_AESKey

        Corp_Id = config.Corp_Id
        Corp_Secret = config.Corp_Secret
        Corp_Agent = config.Corp_Agent
        Corp_Agent_Secret = config.Corp_Agent_Secret

        from wechatpy.enterprise.crypto import WeChatCrypto
        _logger.info('Create crypto: %s %s %s'%(Corp_Token, Corp_AESKey, Corp_Id))
        try:
            self.crypto_handle = WeChatCrypto(Corp_Token, Corp_AESKey, Corp_Id)
        except:
            _logger.error(u'初始化企业微信客户端实例失败，请在微信对接配置中填写好相关信息！')
            if not Corp_Id:
                from_ui = False
            if from_ui:
                raise ValidationError(u'对接失败，请检查相关信息是否填写正确')
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
    dbname = env.cr.dbname
    if dbname not in CorpEnvDict:
        CorpEntry().init(env)
    return CorpEnvDict[env.cr.dbname]
