## Oejia_wx
Odoo 的微信模块，提供了对微信公众号、企业号（企业微信）及小程序的接入与管理，实现了微信消息与Odoo聊天的无缝对接

## 特性
* 用户、组同步管理
* 用户消息对接Odoo聊天
* 高效便捷的推送群组通知消息
* 全功能自定义公众号菜单配置
* 各种返回消息类型的支持
* 灵活配置自动回复及匹配方式
* 统一的公众号素材管理，可便捷地在菜单及自动消息回复中使用
* 支持企业微信审批流消息的接入
* 支持 Odoo 8.0 到 12.0 社区版、企业版, 支持Python2.7、Python3

## 使用
1. 下载源码，安装依赖的python库：wechatpy、pycrypto
2. 将 oejia_wx 放到您Odoo的 addons 目录下，刷新应用列表即可像其他模块一样在应用列表里看到
3. 安装模块，可以看到产生了顶部“微信”主菜单
4. 对接微信配置
```
  对接微信公众号可进入 【微信】/【微信设置】/【公众号对接配置】页面，填写您的公众号 AppId、AppSecret，保存
  将页面的 URL、Token值填写到微信公众号后台“接口配置”的对应的地方，即完成了对接。
  对接企业微信和微信小程序的配置和对接公众号类似
```


详细说明：[http://www.oejia.net/blog/2016/03/12/oejia_wx_base.html](http://www.oejia.net/blog/2016/03/12/oejia_wx_base.html)

企业号功能说明：[http://www.oejia.net/blog/2016/08/12/oejia_wx_corp.html](http://www.oejia.net/blog/2016/08/12/oejia_wx_corp.html)

## 试用

关注官方公众号“oejia客优云”，点击菜单“演示&体验” — “试用微信模块”即可获取测试体验账号

![官方公众号](http://oejia.net/static/img/oejia_gzh.jpg)

Screenshots
========
![info](https://github.com/JoneXiong/oejia_wx/raw/10.0/static/description/2016-01-17_234224.jpg)
![info](https://github.com/JoneXiong/oejia_wx/raw/10.0/static/description/2016-01-17_234349.jpg)
![info](https://github.com/JoneXiong/oejia_wx/raw/10.0/static/description/2016-01-18_200713.jpg)
![info](https://github.com/JoneXiong/oejia_wx/raw/10.0/static/description/2016-01-18_183011.jpg)

## 交流
技术分享
[http://www.oejia.net/](http://www.oejia.net/)

Odoo-OpenERP扩展开发2群：796367461

Odoo-OpenERP扩展开发1群：260160505 (已满)

## 微信模块企业版
特性：
- Odoo端和微信端双向消息推送
- Odoo单据mail消息自动推送微信手机端
- 支持Odoo单据集成企业微信审批流实现移动端审批
- Odoo业务单据变更的自动微信通知
- 支持公众号、微信小程序的客户消息直接通过Odoo后台或企业微信移动端应答

链接：[https://www.calluu.cn/shop/product/odoo-6](https://www.calluu.cn/shop/product/odoo-6)

## 微信客服系统应用
[http://www.oejia.net/blog/2018/05/04/oejia_wx_cs_about.html](http://www.oejia.net/blog/2018/05/04/oejia_wx_cs_about.html)


## 获取商业支持

[https://www.calluu.cn/page/contactus](https://www.calluu.cn/page/contactus)
