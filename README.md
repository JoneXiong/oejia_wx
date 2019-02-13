## Oejia_wx
Odoo 的微信模块，提供了对微信公众号、企业号（企业微信）及小程序的接入与管理，实现了微信消息与Odoo聊天的无缝对接

## 特性
* 用户、组同步管理
* 用户消息对接Odoo聊天
* 高效便捷的推送群组通知消息
* 全功能自定义公众号菜单配置
* 各种返回消息类型的支持
* 灵活配置自动回复及匹配方式
* 统一的公众号素材管理，可便捷地的在菜单及自动消息回复中使用
* 支持企业微信审批流消息的接入
* 支持 Odoo 8.0 到 12.0社区版、企业版, 支持Python2.7、Python3

## 使用
1. 下载源码，安装依赖的python库：wechatpy、pycrypto
2. 将 oejia_wx 放到您Odoo的 addons 目录下，刷新应用列表即可像其他模块一样在应用列表里看到
3. 安装模块，可以看到产生了顶部“微信”主菜单
4. 对接微信配置
```
  对接微信公众号可进入 【微信】/【微信设置】/【公众号对接配置】页面，填写您的公众号 AppId、AppSecret，保存
  将页面的 URL、Token值填写到微信公众号后台“接口配置”的对应的地方，即完成了对接。对接企业微信和微信小程序的配置和对接公众号类似
```


详细说明：[http://www.oejia.net/blog/2016/03/12/oejia_wx_base.html](http://www.oejia.net/blog/2016/03/12/oejia_wx_base.html)

企业号功能说明：[http://www.oejia.net/blog/2016/08/12/oejia_wx_corp.html](http://www.oejia.net/blog/2016/08/12/oejia_wx_corp.html)

## 试用

关注官方公众号“oejia客优云”，点击菜单“演示&体验”即可获取测试体验账号

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

Odoo-OpenERP扩展开发群: 260160505

## 微信模块企业版
特性：
- Odoo端和微信端双向消息推送
- Odoo单据mail消息自动推送微信手机端
- 支持Odoo单据集成企业微信审批流实现移动端审批
- Odoo业务单据变更的自动微信通知
- 支持公众号、微信小程序的客户消息直接通过Odoo后台或企业微信移动端应答

购买链接：[https://www.calluu.cn/shop/product/odoo-6](https://www.calluu.cn/shop/product/odoo-6)

## 微信客服系统应用
[http://www.oejia.net/blog/2018/05/04/oejia_wx_cs_about.html](http://www.oejia.net/blog/2018/05/04/oejia_wx_cs_about.html)


## Change log

### v0.5.0

- 兼容支持 Odoo11
- 消息渠道配置默认值优化
- 请求微信接口异常时的优化
- 添加同步操作的菜单入口
- 增加对微信用户发消息的功能函数

### v0.5.1
- 增加微信聊天会话ID的数据库存储
- 优化聊天会话缓存，防止出现重复的会话记录
- 优化微信RPC操作对象的初始化的管理,兼容多db模式时的使用
- 取消渠道参数的手动配置改为自动关联
- 微信客服默认消息可配置
- 公众号用户会话缓存优化，防止重启后出现重复的会话


## 获取商业支持

购买商业支持会员: [https://www.calluu.cn/shop/product/odoo-vip-5](https://www.calluu.cn/shop/product/odoo-vip-5)
