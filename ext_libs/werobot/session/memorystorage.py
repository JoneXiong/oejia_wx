# -*- coding: utf-8 -*-

from werobot.session import SessionStorage


class MemoryStorage(SessionStorage):
    """
    MemoryStorage 会把你的 Session 数据存到内存当中
    """
    data_dict = None
    
    def __init__(self):
        self.data_dict = {}

    def get(self, id):
        return self.data_dict.get(id, {})

    def set(self, id, value):
        self.data_dict[id] = value

    def delete(self, id):
        del self.data_dict[id]
