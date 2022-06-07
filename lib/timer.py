# coding: UTF-8
# author: 尘
# datetime: 2022/3/21 
# instructions: 
import time


class Timer:
    def __init__(self):
        self._clock = time.time()

    def time(self, task=''):
        temp = time.time()
        print(f'{task}耗时：{temp - self._clock}')
        self._clock = temp


def exec_time(func):
    def wrapper(*args, **kwargs):
        t = time.time()
        func(*args, **kwargs)
        print(f'{str(func)}耗时：{time.time() - t}')
    return wrapper


if __name__ == '__main__':
    @exec_time
    def a():
        time.sleep(1)
        print('a')

    a()