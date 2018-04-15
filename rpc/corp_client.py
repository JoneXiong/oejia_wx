# coding=utf-8
import logging

from wechatpy.enterprise import WeChatClient

_logger = logging.getLogger(__name__)


crypto_handle = None

# 用于agent应用API交互的client
client = None

# 用于通讯录API交互的client
txl_client = None

# 当前Agent
current_agent = None

UUID_OPENID = {}

# 微信用户客服消息的会话缓存
OPENID_UUID = {}

# 微信用户对应的Odoo用户ID缓存
OPENID_UID = {}

# 微信用户(绑定了Odoo用户)和Odoo用户的会话缓存(由Odoo用户发起, key 为 db-uid)
UID_UUID = {}

def init_client(appid, secret):
    global client
    client = WeChatClient(appid, secret)
    return client

def init_txl_client(appid, secret):
    global txl_client
    txl_client = WeChatClient(appid, secret)
    return txl_client

def chat_send(db,uuid, msg):
    #_dict = UUID_OPENID.get(db,None)
    if UUID_OPENID:
        openid = UUID_OPENID.get(uuid,None)
        if openid:
            client.message.send_text(current_agent, openid, msg)
    return -1

def init(env):
    Param = env['ir.config_parameter'].sudo()

    Corp_Token = Param.get_param('Corp_Token') or ''
    Corp_AESKey = Param.get_param('Corp_AESKey') or ''

    Corp_Id = Param.get_param('Corp_Id') or ''       # 企业号
    Corp_Secret = Param.get_param('Corp_Secret') or ''
    Corp_Agent = Param.get_param('Corp_Agent') or ''

    from wechatpy.enterprise.crypto import WeChatCrypto
    global current_agent
    global crypto_handle
    _logger.info('Create crypto: %s %s %s'%(Corp_Token, Corp_AESKey, Corp_Id))
    try:
        crypto_handle = WeChatCrypto(Corp_Token, Corp_AESKey, Corp_Id)
    except:
        _logger.error('初始化微信客户端实例失败，请在微信对接配置中填写好相关信息！')
    init_client(Corp_Id, Corp_Secret)
    init_txl_client(Corp_Id, Corp_Secret)
    current_agent = Corp_Agent

    global OPENID_UUID
    global UUID_OPENID
    users = env['wx.corpuser'].sudo().search([('last_uuid','!=',None)])
    for obj in users:
        OPENID_UUID[obj.userid] = obj.last_uuid
        UUID_OPENID[obj.last_uuid] = obj.userid
    print('corp client init: %s %s'%(OPENID_UUID, UUID_OPENID))
