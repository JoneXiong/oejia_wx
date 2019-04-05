# coding=utf-8

import logging


# 企业号相关
from wechatpy.enterprise.crypto import WeChatCrypto
from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException
from wechatpy.enterprise.exceptions import InvalidCorpIdException
from wechatpy.enterprise import parse_message, create_reply
# 公众号相关
from wechatpy.utils import check_signature

import werkzeug


from openerp import http
from openerp.http import request


_logger = logging.getLogger(__name__)


def abort(code):
    return werkzeug.wrappers.Response('Unknown Error: Application stopped.', status=code, content_type='text/html;charset=utf-8')

class WxCorpHandler(http.Controller):

    def __init__(self):
        from ..rpc import corp_client
        entry = corp_client.CorpEntry()
        entry.init(request.env)
        self.crypto = entry.crypto_handle


    @http.route('/corp_handler', type='http', auth="none", methods=['GET', 'POST'], csrf=False)
    def handle(self, **kwargs):
        msg_signature = request.params.get("msg_signature")
        timestamp = request.params.get("timestamp")
        nonce = request.params.get("nonce")

        echo_str = request.params.get('echostr', '')

        if request.httprequest.method == 'GET':
            try:
                echo_str = self.crypto.decrypt_message(
                    {'Encrypt': echo_str},
                    msg_signature,
                    timestamp,
                    nonce
                )
            except InvalidSignatureException:
                abort(403)
            return echo_str

        # POST
        msg = None
        try:
            msg = self.crypto.decrypt_message(
                request.httprequest.data,
                msg_signature,
                timestamp,
                nonce
            )
        except (InvalidSignatureException, InvalidCorpIdException):
            abort(403)
        msg = parse_message(msg)
        ss = '>>> handle msg: %s %s %s'%(msg.type, msg.id, msg)
        _logger.info(ss)
        ret = ''
        if msg.type in ['text', 'image', 'voice', 'location']:
            #reply = create_reply(msg.content, msg).render()
            from .handlers.text_handler import kf_handler
            ret = kf_handler(request, msg)
        elif msg.type == 'event':
            if msg.event=='subscribe':
                from .handlers.event_handler import subscribe_handler
                ret = subscribe_handler(request, msg)
            elif msg.event=='unsubscribe':
                from .handlers.event_handler import unsubscribe_handler
                ret = unsubscribe_handler(request, msg)
        elif msg.type == 'unknown':
            data = msg._data
            if data.get('Event')=='open_approval_change':
                from .handlers.approval_handler import approval_handler
                approval_handler(request, msg)
        reply = create_reply(ret, msg).render()
        res = self.crypto.encrypt_message(reply, request.params.get("nonce"), request.params.get("timestamp"))
        return res

