# coding=utf-8

from wechatpy.enterprise import WeChatClient

client = None

UUID_OPENID = {}
OPENID_UUID = {}
OPENID_UID = {}
UID_UUID = {}

def init_client(appid, secret):
    global client
    client = WeChatClient(appid, secret)
    return client

def chat_send(db,uuid, msg):
    _dict = UUID_OPENID.get(db,None)
    if _dict:
        openid = _dict.get(uuid,None)
        if openid:
            client.message.send_text(0, openid, msg)
    return -1
