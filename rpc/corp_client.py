# coding=utf-8
import logging

from wechatpy.enterprise import WeChatClient

_logger = logging.getLogger(__name__)


CorpEnvDict = {}

class CorpEntry(object):

    def __init__(self):

        self.crypto_handle = None

        # 用于agent应用API交互的client
        self.client = None

        # 用于通讯录API交互的client
        self.txl_client = None

        # 当前Agent
        self.current_agent = None

        self.UUID_OPENID = {}

        # 微信用户客服消息的会话缓存
        self.OPENID_UUID = {}

        # 微信用户对应的Odoo用户ID缓存
        self.OPENID_UID = {}

        # 企业微信用户(绑定了Odoo用户)和Odoo的会话缓存(由Odoo用户发起, key 为 db-uid)
        self.UID_UUID = {}

    def init_client(self, appid, secret):
        self.client = WeChatClient(appid, secret)
        return self.client

    def init_txl_client(self, appid, secret):
        self.txl_client = WeChatClient(appid, secret)
        return self.txl_client

    def chat_send(self, db, uuid, msg):
        #_dict = UUID_OPENID.get(db,None)
        if self.UUID_OPENID:
            openid = self.UUID_OPENID.get(uuid,None)
            if openid:
                self.client.message.send_text(self.current_agent, openid, msg)
        return -1

    def init(self, env):
        global CorpEnvDict
        CorpEnvDict[env.cr.dbname] = self

        Param = env['ir.config_parameter'].sudo()

        Corp_Token = Param.get_param('Corp_Token') or ''
        Corp_AESKey = Param.get_param('Corp_AESKey') or ''

        Corp_Id = Param.get_param('Corp_Id') or ''       # 企业号
        Corp_Secret = Param.get_param('Corp_Secret') or ''
        Corp_Agent = Param.get_param('Corp_Agent') or ''
        Corp_Agent_Secret = Param.get_param('Corp_Agent_Secret') or ''

        from wechatpy.enterprise.crypto import WeChatCrypto
        _logger.info('Create crypto: %s %s %s'%(Corp_Token, Corp_AESKey, Corp_Id))
        try:
            self.crypto_handle = WeChatCrypto(Corp_Token, Corp_AESKey, Corp_Id)
        except:
            _logger.error(u'初始化微信客户端实例失败，请在微信对接配置中填写好相关信息！')
        self.init_client(Corp_Id, Corp_Agent_Secret)
        self.init_txl_client(Corp_Id, Corp_Secret)
        self.current_agent = Corp_Agent

        try:
            users = env['wx.corpuser'].sudo().search([('last_uuid','!=',None)])
            for obj in users:
                self.OPENID_UUID[obj.userid] = obj.last_uuid
                self.UUID_OPENID[obj.last_uuid] = obj.userid
        except:
            env.cr.rollback()
            import traceback;traceback.print_exc()

        print('corp client init: %s %s'%(self.OPENID_UUID, self.UUID_OPENID))

def corpenv(env):
    return CorpEnvDict[env.cr.dbname]
