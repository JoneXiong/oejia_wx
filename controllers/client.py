# coding=utf-8
import logging

from werobot.client import Client, ClientException
from werobot.robot import BaseRoBot
from werobot.session.memorystorage import MemoryStorage
from werobot.logger import enable_pretty_logging

from openerp import exceptions

_logger = logging.getLogger(__name__)


class WeRoBot(BaseRoBot):
    pass

WeRoBot.message_types.append('file')


WxEnvDict = {}

class WxEntry(object):

    def __init__(self):

        self.wxclient = Client('appid_xxxxxxxxxxxxxxx', 'appsecret_xxxxxxxxxxxxxx')

        self.UUID_OPENID = {}

        # 微信用户客服消息的会话缓存
        self.OPENID_UUID = {}

        self.robot = None

    def send_text(self, openid, text):
        try:
            self.wxclient.send_text_message(openid, text)
        except ClientException as e:
            raise exceptions.UserError(u'发送失败 %s'%e)

    def chat_send(self, uuid, msg):
        openid = self.UUID_OPENID.get(uuid,None)
        if openid:
            self.send_text(openid, msg)

    def upload_media(self, media_type, media_file):
        try:
            return self.wxclient.upload_media(media_type, media_file)
        except ClientException as e:
            raise exceptions.UserError(u'image上传失败 %s'%e)

    def send_image_message(self, openid, media_id):
        try:
            self.wxclient.send_image_message(openid, media_id)
        except ClientException as e:
            raise exceptions.UserError(u'发送image失败 %s'%e)

    def send_image(self, uuid, media_id):
        openid = self.UUID_OPENID.get(uuid, None)
        if openid:
            self.send_image_message(openid, media_id)

    def send_voice(self, uuid, media_id):
        openid = self.UUID_OPENID.get(uuid, None)
        if openid:
            try:
                self.wxclient.send_voice_message(openid, media_id)
            except ClientException as e:
                raise exceptions.UserError(u'发送voice失败 %s'%e)

    def init(self, env):
        dbname = env.cr.dbname
        global WxEnvDict
        if dbname in WxEnvDict:
            del WxEnvDict[dbname]
        WxEnvDict[dbname] = self

        Param = env['ir.config_parameter'].sudo()
        self.wx_token = Param.get_param('wx_token') or ''
        self.wx_appid = Param.get_param('wx_appid') or ''
        self.wx_AppSecret = Param.get_param('wx_AppSecret') or ''

        #robot.config["TOKEN"] = self.wx_token
        self.wxclient.appid = self.wx_appid
        self.wxclient.appsecret = self.wx_AppSecret

        try:
            # 刷新 AccessToken
            self.wxclient._token = None
            _ = self.wxclient.token
        except:
            import traceback;traceback.print_exc()
            _logger.error(u'初始化微信客户端token失败，请在微信对接配置中填写好相关信息！')

        session_storage = MemoryStorage()
        robot = WeRoBot(token=self.wx_token, enable_session=True, logger=_logger, session_storage=session_storage)
        enable_pretty_logging(robot.logger)
        self.robot = robot

        try:
            users = env['wx.user'].sudo().search([('last_uuid','!=',None)])
            for obj in users:
                self.OPENID_UUID[obj.openid] = obj.last_uuid
                self.UUID_OPENID[obj.last_uuid] = obj.openid
        except:
            env.cr.rollback()
            import traceback;traceback.print_exc()

        print('wx client init: %s %s'%(self.OPENID_UUID, self.UUID_OPENID))

def wxenv(env):
    return WxEnvDict[env.cr.dbname]
