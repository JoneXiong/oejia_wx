# coding=utf-8
import logging

from wechatpy.client import WeChatClient
from wechatpy.crypto import WeChatCrypto

from odoo.exceptions import ValidationError, UserError
from odoo import fields

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
        self.subscribe_auto_msg = None

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

    def create_reply(self, ret_msg, message):
        if type(ret_msg)==dict:
            if ret_msg.get('media_type')=='news':
                self.wxclient.send_articles(message.source, ret_msg['media_id'])
            return None
        else:
            return ret_msg

    def init(self, env, from_ui=False):
        self.init_data(env)
        dbname = env.cr.dbname
        global WxEnvDict
        if dbname in WxEnvDict:
            del WxEnvDict[dbname]
        WxEnvDict[dbname] = self

        config = env['wx.config'].sudo().get_cur()
        self.wx_token = config.wx_token
        self.wx_aeskey = config.wx_aeskey
        self.wx_appid = config.wx_appid
        self.wx_AppSecret = config.wx_AppSecret

        if config.action:
            self.subscribe_auto_msg = config.action.get_wx_reply()

        self.client = WeChatClient(self.wx_appid, self.wx_AppSecret, session=self.gen_session())
        self.wxclient = self.client

        try:
            if self.wx_aeskey:
                self.crypto_handle = WeChatCrypto(self.wx_token, self.wx_aeskey, self.wx_appid)
        except:
            _logger.error(u'初始化微信公众号客户端实例失败，请在微信对接配置中填写好相关信息！')
            if not self.wx_appid:
                from_ui = False
            if from_ui:
                raise ValidationError(u'对接失败，请检查相关信息是否填写正确')

        if config.action:
            self.subscribe_auto_msg = config.action.get_wx_reply()

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
    dbname = env.cr.dbname
    if dbname not in WxEnvDict:
        WxEntry().init(env)
    return WxEnvDict[env.cr.dbname]
