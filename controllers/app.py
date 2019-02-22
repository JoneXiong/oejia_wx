# coding=utf-8

import logging

from wechatpy.utils import check_signature
from wechatpy import parse_message
from wechatpy import create_reply
from wechatpy.exceptions import InvalidSignatureException, InvalidAppIdException

import werkzeug


from openerp import http
from openerp.http import request


_logger = logging.getLogger(__name__)


def abort(code):
    return werkzeug.wrappers.Response('Unknown Error: Application stopped.', status=code, content_type='text/html;charset=utf-8')


class WxAppHandler(http.Controller):

    def __init__(self):
        from ..rpc import app_client
        entry = app_client.AppEntry()
        try:
            entry.init(request.env)
        except:
            import traceback;traceback.print_exc()
        self.crypto = entry.crypto_handle
        self.token = entry.token

    @http.route('/app_handler', type='http', auth="none", methods=['GET', 'POST'], csrf=False)
    def handle(self, **kwargs):
        _logger.info('>>> %s'%request.params)
        msg_signature = request.params.get('msg_signature', '')
        timestamp = request.params.get('timestamp', '')
        nonce = request.params.get('nonce', '')

        encrypt_type = request.params.get('encrypt_type', 'raw')

        if request.httprequest.method == 'GET':
            try:
                echo_str = check_signature(
                    self.token,
                    request.params.get('signature', ''),
                    timestamp,
                    nonce
                )
            except InvalidSignatureException:
                return abort(403)
            return request.params.get('echostr', '')

        # POST
        if encrypt_type == 'raw':
            # plaintext mode
            msg = parse_message(request.httprequest.data)
        else:
            # encryption mode
            msg = None
            try:
                msg = self.crypto.decrypt_message(
                    request.httprequest.data,
                    msg_signature,
                    timestamp,
                    nonce
                )
            except (InvalidSignatureException, InvalidAppIdException):
                return abort(403)
            msg = parse_message(msg)

        _logger.info('>>> %s %s'%(msg.type, msg))

        ret = ''
        if msg.type in ['text', 'image', 'voice']:
            from .handlers.app_handler import app_kf_handler
            ret = app_kf_handler(request, msg)

        return 'success'

