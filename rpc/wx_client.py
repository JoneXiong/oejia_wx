# coding=utf-8
import logging

from wechatpy.client import WeChatClient
from wechatpy.crypto import WeChatCrypto
from wechatpy import create_reply
from wechatpy import replies
from wechatpy.fields import StringField

from odoo.exceptions import ValidationError, UserError
from odoo import fields

from .base import EntryBase


_logger = logging.getLogger(__name__)


WxEnvDict = {}

class MpnewsField(StringField):
    def to_xml(self, value):
        value = self.converter(value)
        return f"""<Mpnews>
        <MediaId><![CDATA[{value}]]></MediaId>
        </Mpnews>"""

    @classmethod
    def from_xml(cls, value):
        return value["MediaId"]

@replies.register_reply("image")
class MpnewsReply(replies.BaseReply):

    type = "mpnews"
    mpnews = MpnewsField('Mpnews')

    @property
    def media_id(self):
        return self.mpnews

    @media_id.setter
    def media_id(self, value):
        self.mpnews = value

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

    def create_reply(self, ret, message):
        if type(ret)==dict:
            media = ret
            media_type = media['media_type']
            media_id = media['media_id']
            if media_type=='image':
                return replies.ImageReply(message=message, media_id=media_id)
            elif media_type=='voice':
                return replies.VoiceReply(message=message, media_id=media_id)
            elif media_type=='video':
                return replies.VideoReply(message=message, media_id=media_id)
            elif media_type=='news':
                return MpnewsReply(message=message, media_id=media_id)
            return None
        else:
            return create_reply(ret, message=message)

    def init(self, env, from_ui=False, key=None):
        self.entry_key = key
        self.init_data(env)
        global WxEnvDict
        if key in WxEnvDict:
            del WxEnvDict[key]
        WxEnvDict[key] = self

        config = env['wx.config'].sudo().search([('appkey', '=', key)], limit=1)
        if not config:
            config = env['wx.config'].sudo().get_cur()
        self.entry_id = config.id

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
            users = env['wx.user'].sudo().search([('last_uuid','!=',None), ('config_id', '=', self.entry_id)])
            for obj in users:
                if obj.last_uuid_time:
                    self.recover_uuid(obj.openid, obj.last_uuid, fields.Datetime.from_string(obj.last_uuid_time))
        except:
            env.cr.rollback()
            import traceback;traceback.print_exc()

        print('wx client init: %s %s'%(self.OPENID_UUID, self.UUID_OPENID))
