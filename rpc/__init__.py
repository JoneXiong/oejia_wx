# coding=utf-8
'''远程调用微信服务器'''

import  json
import os

from wechatpy.client.async.tornado import AsyncWeChatClient

APPID = 'wxd7aa56e2c7b1f4f1'
SECRET = '2817b66a1d5829847196cf2f96ab2816'


OPENID = 'ozJS1syaqn5ztglMsr8ceH8o2zCQ'


client = AsyncWeChatClient(APPID, SECRET)


def foo():
    try:
        user_info = yield client.user.get(OPENID)
        print  json.dumps(user_info)
        
        group_id = yield client.user.get_group_id(OPENID)
        print str(group_id)
        
        img_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'doge.jpeg'
        )
        with open(img_path) as media_file:
            res = yield client.media.upload('image', media_file)
            print json.dumps(res)
            
        menu_data = {
            'button': [
                {
                    'type': 'click',
                    'name': 'test',
                    'key': 'test'
                }
            ]
        }
        res = yield client.menu.create(menu_data)
        print json.dumps(res)
        
    except Exception as e:
        print(e)