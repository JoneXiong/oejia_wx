# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import random
from datetime import datetime, timedelta

from wechatpy.pay.utils import get_external_ip
from wechatpy.pay.base import BaseWeChatPayAPI


class WeChatOrder(BaseWeChatPayAPI):

    def create(self, trade_type, body, total_fee, notify_url, client_ip=None,
               user_id=None, out_trade_no=None, detail=None, attach=None,
               fee_type='CNY', time_start=None, time_expire=None,
               goods_tag=None, product_id=None, device_info=None):
        """
        统一下单接口

        :param trade_type: 交易类型，取值如下：JSAPI，NATIVE，APP，WAP
        :param body: 商品描述
        :param total_fee: 总金额，单位分
        :param notify_url: 接收微信支付异步通知回调地址
        :param client_ip: 可选，APP和网页支付提交用户端ip，Native支付填调用微信支付API的机器IP
        :param user_id: 可选，用户在商户appid下的唯一标识。trade_type=JSAPI，此参数必传
        :param out_trade_no: 可选，商户订单号，默认自动生成
        :param detail: 可选，商品详情
        :param attach: 可选，附加数据，在查询API和支付通知中原样返回，该字段主要用于商户携带订单的自定义数据
        :param fee_type: 可选，符合ISO 4217标准的三位字母代码，默认人民币：CNY
        :param time_start: 可选，订单生成时间，默认为当前时间
        :param time_expire: 可选，订单失效时间，默认为订单生成时间后两小时
        :param goods_tag: 可选，商品标记，代金券或立减优惠功能的参数
        :param product_id: 可选，trade_type=NATIVE，此参数必传。此id为二维码中包含的商品ID，商户自行定义
        :param device_info: 可选，终端设备号(门店号或收银设备ID)，注意：PC网页或公众号内支付请传"WEB"
        :return: 返回的结果数据
        """
        now = datetime.now()
        hours_later = now + timedelta(hours=2)
        if time_start is None:
            time_start = now
        if time_expire is None:
            time_expire = hours_later
        if not out_trade_no:
            out_trade_no = '{0}{1}{2}'.format(
                self.mch_id,
                now.strftime('%Y%m%d%H%M%S'),
                random.randint(1000, 10000)
            )
        data = {
            'appid': self.appid,
            'device_info': device_info,
            'body': body,
            'detail': detail,
            'attach': attach,
            'out_trade_no': out_trade_no,
            'fee_type': fee_type,
            'total_fee': total_fee,
            'spbill_create_ip': client_ip or get_external_ip(),
            'time_start': time_start.strftime('%Y%m%d%H%M%S'),
            'time_expire': time_expire.strftime('%Y%m%d%H%M%S'),
            'goods_tag': goods_tag,
            'notify_url': notify_url,
            'trade_type': trade_type,
            'product_id': product_id,
            'openid': user_id,
        }
        return self._post('pay/unifiedorder', data=data)

    def query(self, transaction_id=None, out_trade_no=None):
        """
        查询订单

        :param transaction_id: 微信的订单号，优先使用
        :param out_trade_no: 商户系统内部的订单号，当没提供transaction_id时需要传这个。
        :return: 返回的结果数据
        """
        data = {
            'appid': self.appid,
            'transaction_id': transaction_id,
            'out_trade_no': out_trade_no,
        }
        return self._post('pay/orderquery', data=data)

    def close(self, out_trade_no):
        """
        关闭订单

        :param out_trade_no: 商户系统内部的订单号
        :return: 返回的结果数据
        """
        data = {
            'appid': self.appid,
            'out_trade_no': out_trade_no,
        }
        return self._post('pay/closeorder', data=data)
