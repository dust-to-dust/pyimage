# coding: UTF-8
# author: 尘
# datetime: 2022/3/21 
# instructions: 
import time


class Timer:
    def __init__(self):
        self._clock = time.time()

    def time(self):
        temp = time.time()
        print(f'耗时：{temp - self._clock}')
        self._clock = temp
