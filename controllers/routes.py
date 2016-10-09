# coding=utf-8
import logging
import os

from werobot.robot import BaseRoBot
from werobot.parser import parse_user_msg
from werobot.reply import create_reply
from werobot.logger import enable_pretty_logging
import werkzeug
from werobot.session.memorystorage import MemoryStorage

import openerp
from openerp import http
from openerp.http import request

_logger = logging.getLogger(__name__)
data_dir = openerp.tools.config['data_dir']
session_storage = MemoryStorage()


def abort(code):
    return werkzeug.wrappers.Response('Unknown Error: Application stopped.', status=code, content_type='text/html;charset=utf-8')


class WeRoBot(BaseRoBot):
    pass

robot = WeRoBot(token='K5Dtswpte', enable_session=True, logger=_logger, session_storage=session_storage)
enable_pretty_logging(robot.logger)
    
class WxController(http.Controller):

    ERROR_PAGE_TEMPLATE = """
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf8" />
            <title>Error: {{e.status}}</title>
            <style type="text/css">
              html {background-color: #eee; font-family: sans;}
              body {background-color: #fff; border: 1px solid #ddd;
                    padding: 15px; margin: 15px;}
              pre {background-color: #eee; border: 1px solid #ddd; padding: 5px;}
            </style>
        </head>
        <body>
            <h1>Error: {{e.status}}</h1>
            <p>微信机器人不可以通过 GET 方式直接进行访问。</p>
            <p>想要使用本机器人，请在微信后台中将 URL 设置为 <pre>{{request.url}}</pre> 并将 Token 值设置正确。</p>
        </body>
    </html>
    """
    
    def __init__(self):
        import client
        Param = request.env()['ir.config_parameter']
        robot.config["TOKEN"] = Param.get_param('wx_token') or 'K5Dtswpte'
        client.wxclient.appid = Param.get_param('wx_appid')  or ''
        client.wxclient.appsecret = Param.get_param('wx_AppSecret')  or ''
        
    @http.route('/wx_handler', type='http', auth="none", methods=['GET'])
    def echo(self, **kwargs):
        if not robot.check_signature(
            request.params.get("timestamp"),
            request.params.get("nonce"),
            request.params.get("signature")
        ):
            return abort(403)
        
        return request.params.get("echostr")

    @http.route('/wx_handler', type='http', auth="none", methods=['POST'], csrf=False)
    def handle(self, **kwargs):
        if not robot.check_signature(
            request.params.get("timestamp"),
            request.params.get("nonce"),
            request.params.get("signature")
        ):
            return abort(403)

        body = request.httprequest.data
        message = parse_user_msg(body)
        robot.logger.info("Receive message %s" % message)
        reply = robot.get_reply(message)
        if not reply:
            robot.logger.warning("No handler responded message %s"
                                % message)
            return ''
        #response.content_type = 'application/xml'
        return create_reply(reply, message=message)
