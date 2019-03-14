# coding=utf-8
import json
import logging

_logger = logging.getLogger(__name__)

def approval_handler(request, msg):
    data = msg._data
    agent_id = data.get('AgentID')
    info = data.get('ApprovalInfo')

    third_no = info.get('ThirdNo')
    open_sp_status = info.get('OpenSpStatus')
    #res_model, res_id = third_no.split('-')
    item = None
    try:
        node = info['ApprovalNodes']['ApprovalNode']
        step = info.get('ApproverStep', '0')
        step = int(step)
        if step>0 and open_sp_status!='4':
            if open_sp_status in ['2', '3', '4']:
                step += 1
            if type(node)==list:
                item = node[step-1]['Items']['Item']
            else:
                item = node['Items']['Item']
    except:
        import traceback;traceback.print_exc()
    _logger.info('>>> approval item %s', item)

    record = None
    M = request.env['wx.approval.record'].sudo()
    if item:
        domain = [
            ('agent_id','=',agent_id),
            ('third_no','=',third_no),
            ('step','=',step)
        ]
        if not M.search(domain).exists():
            record = M.create({
                #'res_model': res_model,
                #'res_id': int(res_id),
                'agent_id': agent_id,
                'third_no': third_no,
                'open_sp_status': open_sp_status,
                'user_name': item.get('ItemName'),
                'user_id': item.get('ItemUserid'),
                'user_image': item.get('ItemImage'),
                'user_party': item.get('ItemParty'),
                'full_data': json.dumps(data),
                'speech': item['ItemSpeech'],
                'step': step,
                'item_status': item['ItemStatus'],
            })
    M.update_obj_status(record, third_no, open_sp_status)
