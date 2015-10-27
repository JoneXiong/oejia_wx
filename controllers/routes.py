# coding=utf-8

from mole import route, run
import werkzeug

from openerp import http
from openerp.http import request
import werobot
from werobot.robot import BaseRoBot

# robot = werobot.WeRoBot(token='K5Dtswpte', enable_session=True)
# robot.wsgi

@route('/jone/mole')
def index():
    return 'Hello Mole!'

def abort(code):
    return werkzeug.wrappers.Response('Unknown Error: Application stopped.', status=code, content_type='text/html;charset=utf-8')

# class Home(http.Controller):
# 
#     @http.route('/', type='http', auth="none")
#     def index(self, s_action=None, db=None, **kw):
#         return http.local_redirect('/web', query=request.params, keep_hash=True)
    
class WeRoBot(BaseRoBot, http.Controller):

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

            <p>如果你仍有疑问，请<a href="http://werobot.readthedocs.org/en/%s/">阅读文档</a>
        </body>
    </html>
    """ % werobot.__version__
    app = None

#     @property
#     def wsgi(self):
#         if not self._handlers:
#             raise

    @http.route('/wx_handler', type='http', auth="none", methods=['GET'])
    def echo(self, **kwargs):
        if not self.check_signature(
            request.params.get("timestamp"),
            request.params.get("nonce"),
            request.params.get("signature")
        ):
            return abort(403)
        return request.params.get("echostr")#request.query.echostr

    @http.route('/wx_handler', type='http', auth="none", methods=['POST'])
    def handle(self, **kwargs):
        if not self.check_signature(
            request.params.get("timestamp"),
            request.params.get("nonce"),
            request.params.get("signature")
        ):
            return abort(403)

        body = request.body.read()
        message = parse_user_msg(body)
        logging.info("Receive message %s" % message)
        reply = self.get_reply(message)
        if not reply:
            self.logger.warning("No handler responded message %s"
                                % message)
            return ''
        response.content_type = 'application/xml'
        return create_reply(reply, message=message)


#     def run(self, server=None, host=None,
#             port=None, enable_pretty_logging=True):
#         if enable_pretty_logging:
#             from werobot.logger import enable_pretty_logging
#             enable_pretty_logging(self.logger)
#         if server is None:
#             server = self.config["SERVER"]
#         if host is None:
#             host = self.config["HOST"]
#         if port is None:
#             port = self.config["PORT"]
#         wsgi = self.wsgi
#         m_run(app=self.app,server=server, host=host, port=port)


robot = WeRoBot(token='K5Dtswpte', enable_session=True)
print 'ddddddddddddddddd'