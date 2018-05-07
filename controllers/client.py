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

    def chat_send(self, db,uuid, msg):
        #_dict = self.UUID_OPENID.get(db,None)
        if self.UUID_OPENID:
            openid = self.UUID_OPENID.get(uuid,None)
            if openid:
                self.send_text(openid, msg)
        return -1

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
            _logger.error('初始化微信客户端token失败，请在微信对接配置中填写好相关信息！')

        session_storage = MemoryStorage()
        robot = WeRoBot(token=self.wx_token, enable_session=True, logger=_logger, session_storage=session_storage)
        enable_pretty_logging(robot.logger)
        self.robot = robot

        users = env['wx.user'].sudo().search([('last_uuid','!=',None)])
        for obj in users:
            self.OPENID_UUID[obj.openid] = obj.last_uuid
            self.UUID_OPENID[obj.last_uuid] = obj.openid
        print('wx client init: %s %s'%(self.OPENID_UUID, self.UUID_OPENID))

def wxenv(env):
    return WxEnvDict[env.cr.dbname]
