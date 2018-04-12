## Oejia_wx
Odoo 的微信模块，提供了对微信公众号和企业号的接入与管理，实现了微信消息与Odoo聊天的无缝对接

## 特性
* 用户、组同步管理
* 用户消息对接chat 一对一实时聊天
* 高效便捷的推送群组通知消息
* 全功能自定义菜单配置
* 各种返回消息类型的支持
* 灵活配置自动回复及匹配方式

## 使用
1. 下载源码
2. 将整个oejia_wx目录放到你的addons目录下，即可像其他模块一样在应用列表里看到了，
3. 安装模块，可以看到产生了顶部“微信”主菜单
4. 对接微信公众号配置
```
  进入 微信/微信设置/对接配置 页面，填写你的公众号 AppId、AppSecret，保存
  将页面自动显示的 URL、Token值填写到微信公众号后台“接口配置”的对应的地方，即完成了对接
```
注：v0.3及以上版本由于包含微信企业号功能请先安装依赖的python包：pycrypto（或cryptography）

详细说明：[http://www.oejia.net/blog/2016/03/12/oejia_wx_base.html](http://www.oejia.net/blog/2016/03/12/oejia_wx_base.html)

企业号功能说明：[http://www.oejia.net/blog/2016/08/12/oejia_wx_corp.html](http://www.oejia.net/blog/2016/08/12/oejia_wx_corp.html)


Screenshots
========
![info](https://github.com/JoneXiong/oejia_wx/raw/master/static/description/2016-01-17_234224.jpg)
![info](https://github.com/JoneXiong/oejia_wx/raw/master/static/description/2016-01-17_234349.jpg)
![info](https://github.com/JoneXiong/oejia_wx/raw/master/static/description/2016-01-18_200713.jpg)
![info](https://github.com/JoneXiong/oejia_wx/raw/master/static/description/2016-01-18_183011.jpg)

## 交流
技术分享
[http://www.oejia.net/](http://www.oejia.net/)

Odoo-OpenERP扩展开发群: 260160505

## 微信模块企业版
特性：
- Odoo端和微信端双向消息推送
- 扫码授权登录支持
- 移动端网页授权登录支持(免密码登录) 
- Odoo业务单据变更的自动微信通知（基于mail模块的订阅机制实现）

购买链接：[https://www.calluu.cn/shop/product/odoo-6](https://www.calluu.cn/shop/product/odoo-6)

## Change log

### v0.5.0

- 兼容支持 Odoo11
- 消息渠道配置默认值优化
- 请求微信接口异常时的优化
- 添加同步操作的菜单入口
- 增加对微信用户发消息的功能函数

## 获取商业支持

购买商业支持会员: [https://www.calluu.cn/shop/product/odoo-vip-5](https://www.calluu.cn/shop/product/odoo-vip-5)
