# Coding: UTF-8
# Author: 尘
# Datetime: 2021/8/27 
# DebugInfo: 


class QueueFIFO:
    """线程不安全"""
    def __init__(self, max_len):
        self.max_len = max_len
        self.queue = []
        self.count = 0
        # 填充队列到指定长度
        for _ in range(max_len):
            self.queue.append(None)

    def put(self, data):
        """append"""
        self.queue.append(data)
        # self.count += 1     # 移动队头指针
        self.queue = self.queue[1:]

    def extend(self, data):
        self.queue.extend(data)
        self.queue = self.queue[len(data):]

    def get(self):
        self.queue.append(None)
        d = self.queue[0]
        self.queue = self.queue[1:]
        return d

    def get_all(self) -> list:
        return self.queue.copy()

