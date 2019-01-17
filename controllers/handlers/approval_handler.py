# coding=utf-8
import json


def approval_handler(request, msg):
    data = msg._data
    agent_id = data.get('AgentID')
    info = data.get('ApprovalInfo')

    third_no = info.get('ThirdNo')
    open_sp_status = info.get('OpenSpStatus')
    res_model, res_id = third_no.split('-')
    record = request.env['wx.approval.record'].sudo().create({
        'res_model': res_model,
        'res_id': int(res_id),
        'agent_id': agent_id,
        'third_no': third_no,
        'open_sp_status': open_sp_status,
        'user_name': info.get('ApplyUserName'),
        'user_id': info.get('ApplyUserId'),
        'user_image': info.get('ApplyUserImage'),
        'user_party': info.get('ApplyUserParty'),
        'full_data': json.dumps(data)
    })
