# coding=utf-8
import logging
import os

from werobot.parser import parse_user_msg
from werobot.reply import create_reply
from werobot.utils import is_string
import werkzeug

import openerp
from openerp import http
from openerp.http import request

_logger = logging.getLogger(__name__)


def abort(code):
    return werkzeug.wrappers.Response('Unknown Error: Application stopped.', status=code, content_type='text/html;charset=utf-8')


class WxController(http.Controller):

    def __init__(self):
        from . import client
        entry = client.WxEntry()
        entry.init(request.env)
        robot = entry.robot
        self.robot = robot
        from .handlers import sys_event
        from .handlers import auto_reply
        from .handlers import menu_click
        sys_event.main(robot)
        auto_reply.main(robot)
        menu_click.main(robot)


    @http.route('/wx_handler', type='http', auth="none", methods=['GET'])
    def echo(self, **kwargs):
        if not self.robot.check_signature(
            request.params.get("timestamp"),
            request.params.get("nonce"),
            request.params.get("signature")
        ):
            return abort(403)

        return request.params.get("echostr")

    @http.route('/wx_handler', type='http', auth="none", methods=['POST'], csrf=False)
    def handle(self, **kwargs):
        if not self.robot.check_signature(
            request.params.get("timestamp"),
            request.params.get("nonce"),
            request.params.get("signature")
        ):
            return abort(403)

        body = request.httprequest.data
        message = parse_user_msg(body)
        self.robot.logger.info("Receive message %s" % message)
        reply = self.robot.get_reply(message)
        if not reply:
            self.robot.logger.warning("No handler responded message %s"
                                % message)
            return ''
        _logger.info('>>> reply: %s'%reply)
        return reply

