# coding=utf-8
import logging

from wechatpy.client import WeChatClient
from wechatpy.crypto import WeChatCrypto

from odoo import exceptions

from .base import EntryBase


_logger = logging.getLogger(__name__)


WxEnvDict = {}

class WxEntry(EntryBase):
    '''
    目前仅公众号发送模板消息使用
    '''

    def __init__(self):
        self.client = None
        self.wxclient = None
        self.crypto_handle = None
        self.token = None

        super(WxEntry, self).__init__()

    def upload_media(self, media_type, media_file):
        return self.client.media.upload(media_type, media_file)

    def chat_send(self, uuid, msg):
        openid = self.get_openid_from_uuid(uuid)
        if openid:
            self.client.message.send_text(openid, msg)

    def send_image(self, uuid, media_id):
        openid = self.get_openid_from_uuid(uuid)
        if openid:
            self.client.message.send_image(openid, media_id)

    def send_voice(self, uuid, media_id):
        openid = self.get_openid_from_uuid(uuid)
        if openid:
            self.client.message.send_video(openid, media_id)

    def init(self, env):
        dbname = env.cr.dbname
        global WxEnvDict
        if dbname in WxEnvDict:
            del WxEnvDict[dbname]
        WxEnvDict[dbname] = self

        Param = env['ir.config_parameter'].sudo()
        self.wx_token = Param.get_param('wx_token') or ''
        self.wx_aeskey = Param.get_param('wx_aeskey') or ''
        self.wx_appid = Param.get_param('wx_appid') or ''
        self.wx_AppSecret = Param.get_param('wx_AppSecret') or ''

        self.client = WeChatClient(self.wx_appid, self.wx_AppSecret)
        self.wxclient = self.client

        try:
            if self.wx_aeskey:
                self.crypto_handle = WeChatCrypto(self.wx_token, self.wx_aeskey, self.wx_appid)
        except:
            _logger.error(u'初始化微信公众号客户端实例失败，请在微信对接配置中填写好相关信息！')

        try:
            users = env['wx.user'].sudo().search([('last_uuid','!=',None)])
            for obj in users:
                if obj.last_uuid_time:
                    self.recover_uuid(obj.openid, obj.last_uuid, fields.Datetime.from_string(obj.last_uuid_time))
        except:
            env.cr.rollback()
            import traceback;traceback.print_exc()

        print('wx client init: %s %s'%(self.OPENID_UUID, self.UUID_OPENID))

def wxenv(env):
    return WxEnvDict[env.cr.dbname]
