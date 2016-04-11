# coding=utf-8

from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException
from wechatpy.enterprise.exceptions import InvalidCorpIdException
from wechatpy.enterprise import parse_message, create_reply

from wechatpy.utils import check_signature

import werkzeug

import openerp
from openerp import http
from openerp.http import request


TOKEN = ''
EncodingAESKey = ''
CorpId = ''

crypto = None

def abort(code):
    return werkzeug.wrappers.Response('Unknown Error: Application stopped.', status=code, content_type='text/html;charset=utf-8')

class WxCorpHandler(http.Controller):
    
    def __init__(self):
        Param = request.env()['ir.config_parameter']
        
        self.TOKEN = Param.get_param('wx_token') or 'K5Dtswpte'
        self.EncodingAESKey = Param.get_param('EncodingAESKey') or ''
        self.CorpId = Param.get_param('CorpId') or ''       # 企业号
        
        global crypto
        crypto = WeChatCrypto(self.TOKEN, self.EncodingAESKey, self.CorpId)
        
    @http.route('/wx_handler', type='http', auth="none", methods=['GET'])
    def echo(self, **kwargs):
        try:
            echo_str = crypto.check_signature(
                request.params.get("msg_signature"),    #新增
                request.params.get("timestamp"),
                request.params.get("nonce"),
                request.params.get("echostr")
            )
        except InvalidSignatureException:
            abort(403)
        return echo_str
    
    @http.route('/wx_handler', type='http', auth="none", methods=['GET', 'POST'])
    def handle(self, **kwargs):
        msg_signature = request.params.get("msg_signature")
        timestamp = request.params.get("timestamp")
        nonce = request.params.get("nonce")
        
        echo_str = request.params.get('echostr', '')
        
        if request.method == 'GET':
            try:
                echo_str = crypto.check_signature(
                    msg_signature,    #新增
                    timestamp,
                    nonce,
                    echo_str
                )
            except InvalidSignatureException:
                abort(403)
        
        # POST
        try:
            msg = crypto.decrypt_message(
                request.httprequest.data,
                msg_signature,
                timestamp,
                nonce
            )
        except (InvalidSignatureException, InvalidCorpIdException):
            abort(403)
        
        msg = parse_message(msg)
        if msg.type == 'text':
            reply = create_reply(msg.content, msg).render()
        else:
            reply = create_reply('Can not handle this for now', msg).render()
        res = crypto.encrypt_message(reply, request.params.get("nonce"), request.params.get("timestamp"))
        return res
    
    
class WxAppHandler(http.Controller):
    
    def __init__(self):
        Param = request.env()['ir.config_parameter']
        
        self.TOKEN = Param.get_param('wx_token') or 'K5Dtswpte'
        self.AES_KEY = Param.get_param('AES_KEY') or ''
        self.APPID = Param.get_param('APPID') or '' # 公众号
    
    @http.route('/wx_handler', type='http', auth="none", methods=['GET', 'POST'])
    def handle_encrypt(self, **kwargs):
        msg_signature = request.params.get('msg_signature', '')
        signature = request.params.get('signature', '')
        timestamp = request.params.get('timestamp', '')
        nonce = request.params.get('nonce', '')
        
        encrypt_type = request.params.get('encrypt_type', 'raw')
        
        echo_str = request.args.get('echostr', '')
        
        try:
            check_signature(self.TOKEN, signature, timestamp, nonce)
        except InvalidSignatureException:
            abort(403)
            
        if request.method == 'GET':
            return echo_str
        
        # POST
        if encrypt_type == 'raw':
            # plaintext mode
            msg = parse_message(request.httprequest.data)
            if msg.type == 'text':
                reply = create_reply(msg.content, msg)
            else:
                reply = create_reply('Sorry, can not handle this for now', msg)
            return reply.render()
        else:
            # encryption mode
            from wechatpy.crypto import WeChatCrypto
    
            crypto = WeChatCrypto(self.TOKEN, self.AES_KEY, self.APPID)   # 公众号
            try:
                msg = crypto.decrypt_message(
                    request.httprequest.data,
                    msg_signature,
                    timestamp,
                    nonce
                )
            except (InvalidSignatureException, InvalidAppIdException):
                abort(403)
            else:
                msg = parse_message(msg)
                if msg.type == 'text':
                    reply = create_reply(msg.content, msg)
                else:
                    reply = create_reply('Sorry, can not handle this for now', msg)
                return crypto.encrypt_message(reply.render(), nonce, timestamp)

