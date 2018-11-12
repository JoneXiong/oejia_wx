# coding=utf-8
import json
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class WxMedia(models.Model):

    _name = 'wx.media'
    _description = u'微信素材'

    media_id = fields.Char('素材ID')
    media_type = fields.Selection([("image", '图片'),("video", '视频'), ("voice", '语音'), ("news", '图文')], string=u'类型')
    name = fields.Char('名称')
    update_time = fields.Char('更新时间')
    url = fields.Char('Url')
    news_item = fields.Text('内容')

    @api.model
    def sync_type(self, media_type):
        from ..controllers import client
        entry = client.wxenv(self.env)
        c_total = 0
        c_flag = 0
        offset = 0
        while True:
            from werobot.client import ClientException
            try:
                data_dict= entry.wxclient.get_media_list(media_type, offset, 20)
            except ClientException as e:
                raise ValidationError(u'微信服务请求异常，异常信息: %s'%e)
            c_total = data_dict['total_count']
            m_count = data_dict['item_count']
            offset += m_count
            _logger.info('get %s media'%m_count)
            if m_count>0:
                items = data_dict["item"]
                for item in items:
                    c_flag +=1
                    media_id = item["media_id"]
                    _logger.info('total %s  now sync the %srd %s .'%(c_total, c_flag, media_id))
                    rs = self.search( [('media_id', '=', media_id)] )
                    if rs.exists():
                        pass
                    else:
                        item["media_type"] = media_type
                        if "news_item" in item:
                            item["news_item"] = json.loads(item["news_item"])
                        self.create(item)
            else:
                break

        _logger.info('sync total: %s'%c_flag)


    @api.model
    def sync(self):
        self.sync_type("image")
        self.sync_type("video")
        self.sync_type("voice")
        self.sync_type("news")

    @api.model
    def sync_confirm(self):
        new_context = dict(self._context) or {}
        new_context['default_info'] = "此操作可能需要一定时间，确认同步吗？"
        new_context['default_model'] = 'wx.media'
        new_context['default_method'] = 'sync'

        return {
            'name': u'确认同步公众号素材',
            'type': 'ir.actions.act_window',
            'res_model': 'wx.confirm',
            'res_id': None,
            'view_mode': 'form',
            'view_type': 'form',
            'context': new_context,
            'view_id': self.env.ref('oejia_wx.wx_confirm_view_form').id,
            'target': 'new'
        }
