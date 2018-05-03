# coding=utf-8

from ...rpc import corp_client

def subscribe_handler(request, message):
    openid = message.source
    entry = corp_client.corpenv(request.env)
    info = entry.client.user.get(openid)
    info['gender'] = int(info['gender'])
    env = request.env()
    rs = env['wx.corpuser'].sudo().search( [('userid', '=', openid)] )
    if not rs.exists():
        info['_from_subscribe'] = True
        obj = env['wx.corpuser'].sudo().create(info)
        _id = obj.id
    else:
        rs.write({'avatar': info.get('avatar',''), 'status': 1})
        _id = rs[0]
    mobile = info.get('mobile', None)
    email = info.get('email', None)
    if mobile or email:
        if mobile and email:
            Q = [ '|', ('mobile', '=', mobile), ('email', '=', email)]
        else:
            Q = [('mobile', '=', mobile)] if mobile else [('email', '=', email)]
        rs = env['res.partner'].sudo().search(Q)
        if rs.exists():
            rs.write({'wxcorp_user_id': _id})
    
    return "您终于来了！欢迎关注"

def unsubscribe_handler(request, message):
    openid = message.source
    env = request.env()
    rs = env['wx.corpuser'].sudo().search( [('userid', '=', openid)] )
    if rs.exists():
        rs.unlink()
    
    return "欢迎下次光临！"
