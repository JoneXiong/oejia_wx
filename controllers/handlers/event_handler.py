# coding=utf-8


def subscribe_handler(request, message):
    openid = message.source
    entry = request.env['wx.corp.config'].corpenv()
    info = entry.client.user.get(openid)
    info['gender'] = str(info['gender'])
    if 'status' in info:
        info['status'] = str(info['status'])
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
        rs.write({'status': '4'})

    return "欢迎下次光临！"
