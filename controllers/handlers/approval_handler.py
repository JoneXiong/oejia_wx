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
    approval_nodes = info['ApprovalNodes']
    #res_model, res_id = third_no.split('-')
    item = None
    record_index = None
    task_item = None
    try:
        node = info['ApprovalNodes']['ApprovalNode']
        if type(node)!=list:
            node = [node]
        step = info.get('ApproverStep', '0')
        step = int(step)
        if open_sp_status!='4' and node:
            if open_sp_status in ['2', '3']:
                # 已通过/已驳回
                task_item = None
                record_index = step
                item = node[record_index]
            else:
                task_item = node[step]
                record_index = step - 1
                item = None if record_index<0 else node[record_index]
    except:
        import traceback;traceback.print_exc()

    record = None
    M = request.env['wx.approval.record'].sudo()

    items = []
    _logger.info('>>> record %s', item)
    if item:
        items = item['Items']['Item']
        if type(items)!=list:
            items = [items]

    task_items = []
    _logger.info('>>> task %s', task_item)
    if task_item:
        task_items = task_item['Items']['Item']
        if type(task_items)!=list:
            task_items = [task_items]

    for item in items:
        domain = [
            ('agent_id','=',agent_id),
            ('third_no','=',third_no),
            ('user_id','=',item.get('ItemUserId')),
            ('step','=',record_index)
        ]
        M.search(domain).write({'item_status': item['ItemStatus']})

    new_records = []
    for item in task_items:
        domain = [
            ('agent_id','=',agent_id),
            ('third_no','=',third_no),
            ('user_id','=',item.get('ItemUserId')),
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
                'user_id': item.get('ItemUserId'),
                'user_image': item.get('ItemImage'),
                'user_party': item.get('ItemParty'),
                'apply_user_name': item.get('ApplyUserName'),
                'apply_user_id': item.get('ApplyUserId'),
                'apply_user_image': item.get('ApplyUserImage'),
                'apply_user_party': item.get('ApplyUserParty'),
                'full_data': json.dumps(data),
                'speech': item['ItemSpeech'],
                'step': step,
                'item_status': item['ItemStatus'],
            })
            new_records.append(record)
    M.update_obj_status(new_records, third_no, open_sp_status, agent_id, approval_nodes)
