# coding=utf-8
import re
import logging
# import urllib
from openerp.http import request
import openerp
from .. import client

_logger = logging.getLogger(__name__)


def main(robot):
    @robot.text
    def input_handle(message, session):
        from .. import client
        entry = client.wxenv(request.env)
        client = entry
        content = message.content.lower()
        serviceid = message.target
        openid = message.source
        _logger.info('>>> wx text msg: %s' % content)

        rs = request.env()['wx.autoreply'].sudo().search([])
        for rc in rs:
            if rc.type == 1:
                if content == rc.key:
                    return rc.action.get_wx_reply()
            elif rc.type == 2:
                if rc.key in content:
                    return rc.action.get_wx_reply()
            elif rc.type == 3:
                try:
                    flag = re.compile(rc.key).match(content)
                except:
                    flag = False
                if flag:
                    return rc.action.get_wx_reply()
        # 客服对话
        uuid = client.OPENID_UUID.get(openid, None)
        ret_msg = ''
        cr, uid, context, db = request.cr, request.uid or openerp.SUPERUSER_ID, request.context, request.db

        if not uuid:
            rs = request.env['wx.user'].sudo().search([('openid', '=', openid)])
            if not rs.exists():
                info = client.wxclient.get_user_info(openid)
                info['group_id'] = ''
                wx_user = request.env['wx.user'].sudo().create(info)
            else:
                wx_user = rs[0]
            anonymous_name = wx_user.nickname

            channel = request.env.ref('oejia_wx.channel_wx')
            channel_id = channel.id

            session_info, ret_msg = request.env["im_livechat.channel"].create_mail_channel(channel_id, anonymous_name,
                                                                                           content)
            if session_info:
                uuid = session_info['uuid']
                client.OPENID_UUID[openid] = uuid
                client.UUID_OPENID[uuid] = openid
                wx_user.write({'last_uuid': uuid})
                request.env['wx.user.uuid'].sudo().create({'openid': openid, 'uuid': uuid})

        if uuid:
            message_type = "message"
            message_content = message.content
            request_uid = request.session.uid or openerp.SUPERUSER_ID
            author_id = False  # message_post accept 'False' author_id, but not 'None'
            if request.session.uid:
                author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id
            mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
            message = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(
                author_id=author_id, email_from=False, body=message_content, message_type='comment',
                subtype='mail.mt_comment', content_subtype='plaintext')

        return ret_msg

    @robot.image
    def input_handle(message, session):
        from .. import client
        from odoo import http
        from odoo.http import request
        import os
        import datetime
        import random
        import urllib
        entry = client.wxenv(request.env)
        client = entry
        content = message.img
        _logger.info('>>> wx get img: %s' % content)
        pic_url = content
        headers = {
            'Accept': 'textml,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'Cache-Control': 'no-cache',
            'Host': 'mmbiz.qpic.cn',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }
        request_data = urllib.request.Request(pic_url, headers=headers)
        try:
            response = urllib.request.urlopen(request_data, timeout=50)
            status = response.getcode()
            _logger.info('>>> wx get img: %s' % status)
        except urllib.request.HTTPError as e:
            print(e.code)
        img_bytes = response.read()
        addons_path = http.addons_manifest['oejia_wx']['addons_path']
        now_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前时间
        random_num = random.randint(0, 100)  # 生成的随机整数n，其中0<=n<=100
        if random_num <= 10:
            random_num = str(0) + str(random_num)
        filename = str(now_time) + str(random_num) + '.jpg'
        img_path_name = os.path.join(addons_path, 'oejia_wx', 'static', 'src', 'img', filename)
        f = open(img_path_name, 'wb+')
        f.write(img_bytes)
        f.close()
        openid = message.source

        # 客服对话
        uuid = client.OPENID_UUID.get(openid, None)
        ret_msg = ''
        cr, uid, context, db = request.cr, request.uid or openerp.SUPERUSER_ID, request.context, request.db

        if not uuid:
            rs = request.env['wx.user'].sudo().search([('openid', '=', openid)])
            if not rs.exists():
                info = client.wxclient.get_user_info(openid)
                info['group_id'] = ''
                wx_user = request.env['wx.user'].sudo().create(info)
            else:
                wx_user = rs[0]
            anonymous_name = wx_user.nickname

            channel = request.env.ref('oejia_wx.channel_wx')
            channel_id = channel.id

            session_info, ret_msg = request.env["im_livechat.channel"].create_mail_channel(channel_id, anonymous_name,
                                                                                           content)
            if session_info:
                uuid = session_info['uuid']
                client.OPENID_UUID[openid] = uuid
                client.UUID_OPENID[uuid] = openid
                wx_user.write({'last_uuid': uuid})
                request.env['wx.user.uuid'].sudo().create({'openid': openid, 'uuid': uuid})

        if uuid:
            web_filename = os.path.join('/oejia_wx', 'static', 'src', 'img', filename)
            message_content = "<img src=\"" + web_filename + "\">"
            request_uid = request.session.uid or openerp.SUPERUSER_ID
            author_id = False  # message_post accept 'False' author_id, but not 'None'
            if request.session.uid:
                author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id
            mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
            message = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(
                author_id=author_id, email_from=False, body=message_content, message_type='comment',
                subtype='mail.mt_comment', content_subtype='html')

        return ret_msg

    @robot.voice
    def input_handle(message, session):
        from .. import client
        from odoo import http
        from odoo.http import request
        import os
        import datetime
        import random
        import urllib
        entry = client.wxenv(request.env)
        client = entry
        content = message.type
        serviceid = message.target
        openid = message.source
        _logger.info('>>> wx text msg: %s' % content)
        wx_token = client.wxclient._token
        voice_id = message.media_id
        voice_url = "http://file.api.weixin.qq.com/cgi-bin/media/get?" + "access_token=" + wx_token + "&" + "media_id=" + voice_id
        print(voice_url)
        try:
            response = urllib.request.urlopen(voice_url, timeout=50)
            status = response.getcode()
            _logger.info('>>> wx get img: %s' % status)
        except urllib.request.HTTPError as e:
            print(e.code)
        voice_bytes = response.read()
        addons_path = http.addons_manifest['oejia_wx']['addons_path']
        now_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # 生成当前时间
        random_num = random.randint(0, 100)  # 生成的随机整数n，其中0<=n<=100
        if random_num <= 10:
            random_num = str(0) + str(random_num)
        filename = str(now_time) + str(random_num) + '.mp4'
        img_path_name = os.path.join(addons_path, 'oejia_wx', 'static', 'src', 'img', filename)

        # 客服对话
        uuid = client.OPENID_UUID.get(openid, None)
        ret_msg = ''
        cr, uid, context, db = request.cr, request.uid or openerp.SUPERUSER_ID, request.context, request.db

        if not uuid:
            rs = request.env['wx.user'].sudo().search([('openid', '=', openid)])
            if not rs.exists():
                info = client.wxclient.get_user_info(openid)
                info['group_id'] = ''
                wx_user = request.env['wx.user'].sudo().create(info)
            else:
                wx_user = rs[0]
            anonymous_name = wx_user.nickname

            channel = request.env.ref('oejia_wx.channel_wx')
            channel_id = channel.id

            session_info, ret_msg = request.env["im_livechat.channel"].create_mail_channel(channel_id, anonymous_name,
                                                                                           content)
            if session_info:
                uuid = session_info['uuid']
                client.OPENID_UUID[openid] = uuid
                client.UUID_OPENID[uuid] = openid
                wx_user.write({'last_uuid': uuid})
                request.env['wx.user.uuid'].sudo().create({'openid': openid, 'uuid': uuid})

        if uuid:
            message_content = 'Sorry,本信息为语音信息，无法接收，请告知客户发送文字信息'
            request_uid = request.session.uid or openerp.SUPERUSER_ID
            author_id = False  # message_post accept 'False' author_id, but not 'None'
            if request.session.uid:
                author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id
            mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
            message = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(
                author_id=author_id, email_from=False, body=message_content, message_type='comment',
                subtype='mail.mt_comment', content_subtype='plaintext')

        return ret_msg

    # 文件信息，目前找不到接收的接口
    @robot.file
    def input_handle(message, session):
        from .. import client
        from odoo.http import request
        entry = client.wxenv(request.env)
        client = entry
        content = message.Title
        _logger.info('>>> wx get file: %s' % message)

        openid = message.source

        # 客服对话
        uuid = client.OPENID_UUID.get(openid, None)
        ret_msg = ''
        cr, uid, context, db = request.cr, request.uid or openerp.SUPERUSER_ID, request.context, request.db

        if not uuid:
            rs = request.env['wx.user'].sudo().search([('openid', '=', openid)])
            if not rs.exists():
                info = client.wxclient.get_user_info(openid)
                info['group_id'] = ''
                wx_user = request.env['wx.user'].sudo().create(info)
            else:
                wx_user = rs[0]
            anonymous_name = wx_user.nickname

            channel = request.env.ref('oejia_wx.channel_wx')
            channel_id = channel.id

            session_info, ret_msg = request.env["im_livechat.channel"].create_mail_channel(channel_id, anonymous_name,
                                                                                           content)
            if session_info:
                uuid = session_info['uuid']
                client.OPENID_UUID[openid] = uuid
                client.UUID_OPENID[uuid] = openid
                wx_user.write({'last_uuid': uuid})
                request.env['wx.user.uuid'].sudo().create({'openid': openid, 'uuid': uuid})

        if uuid:
            message_content = 'Sorry,本信息为文件，无法接收，请告知客户'
            request_uid = request.session.uid or openerp.SUPERUSER_ID
            author_id = False  # message_post accept 'False' author_id, but not 'None'
            if request.session.uid:
                author_id = request.env['res.users'].sudo().browse(request.session.uid).partner_id.id
            mail_channel = request.env["mail.channel"].sudo(request_uid).search([('uuid', '=', uuid)], limit=1)
            message = mail_channel.sudo(request_uid).with_context(mail_create_nosubscribe=True).message_post(
                author_id=author_id, email_from=False, body=message_content, message_type='comment',
                subtype='mail.mt_comment', content_subtype='plaintext')

        return ret_msg

    # 响应事件,例如: KeyError: 'templatesendjobfinish'
    @robot.templatesendjobfinish
    def input_handle(message):
        return True
