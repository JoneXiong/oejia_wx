# coding=utf-8
import logging
import datetime


from wechatpy.client import WeChatClient
from wechatpy.crypto import WeChatCrypto
from openerp.exceptions import ValidationError, UserError

from .base import EntryBase


_logger = logging.getLogger(__name__)


AppEnvDict = {}

class AppEntry(EntryBase):

    def __init__(self):

        self.client = None
        self.crypto_handle = None
        self.token = None

        super(AppEntry, self).__init__()

    def upload_media(self, media_type, media_file):
        #return self.client.media.upload_mass_image(media_file[1])
        return self.client.media.upload(media_type, media_file)

    def chat_send(self, uuid, msg):
        openid = self.get_openid_from_uuid(uuid)
        if openid:
            self.client.message.send_text(openid, msg)

    def send_image(self, uuid, media_id):
        openid = self.get_openid_from_uuid(uuid)
        if openid:
            return self.client.message.send_image(openid, media_id)

    def init(self, env, from_ui=False):
        self.init_data(env)
        dbname = env.cr.dbname
        global AppEnvDict
        if dbname in AppEnvDict:
            del AppEnvDict[dbname]
        AppEnvDict[dbname] = self

        #Param = env['ir.config_parameter'].sudo()
        config = env['wx.app.config'].sudo().get_cur()

        Token = config.token
        AESKey = config.aeskey
        AppID = config.app_id
        AppSecret = config.secret

        self.client = WeChatClient(AppID, AppSecret, session=self.gen_session())
        self.token = Token

        _logger.info('Create crypto: %s %s %s'%(Token, AESKey, AppID))
        try:
            self.crypto_handle = WeChatCrypto(Token, AESKey, AppID)
        except:
            _logger.error(u'初始化微信小程序客户端实例失败，请在微信对接配置中填写好相关信息！')
            if not AppID:
                from_ui = False
            if from_ui:
                raise ValidationError(u'对接失败，请检查相关信息是否填写正确')

def appenv(env):
    dbname = env.cr.dbname
    if dbname not in AppEnvDict:
        AppEntry().init(env)
    return AppEnvDict[env.cr.dbname]
