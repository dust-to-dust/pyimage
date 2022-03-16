# Coding: UTF-8
# Author: 尘
# Datetime: 2021/7/29 
# DebugInfo: 

import threading as t
from queue import Queue     # 线程安全，dqueue的高级封装
from typing import List
from time import sleep
from tqdm import tqdm


# from sys import exit


class Thread(t.Thread):
    def __init__(self, tasks: Queue, exceptions: list):
        super(Thread, self).__init__()
        self.tasks = tasks
        self.exceptions = exceptions    # 函数 参数 异常

    def run(self):
        # 执行任务中调用exit会结束线程，不会回池
        # 死循环，从而让创建的线程在一定条件下关闭退出
        task = None
        while 1:
            try:
                task = self.tasks.get()  # 队列为空时阻塞
                if task is None:
                    break
                if len(task) == 1:
                    task[0]()
                else:
                    task[0](*task[1:])  # 执行任务，未接收返回值
            except (Exception, SystemExit) as e:
                # 捕捉多异常时应该以元组形式表示
                self.exceptions.append((*task, e))


class ThreadPool:
    def __init__(self, max_workers=8, retry=1, print_exc=True):
        self.is_running = True
        self.timer = None
        self.print_exc = print_exc
        self.retry = retry  # 将发生错误的任务重新执行retry次
        self.tasks = Queue()
        self.task_count = 0  # 总共提交的任务数
        self.exceptions = []  # 发生异常的 任务、参数 以及 异常
        self.thread_list: List[Thread] = []

        for _ in range(max_workers):
            thread = Thread(self.tasks, self.exceptions)
            self.thread_list.append(thread)
            thread.start()

    def submit(self, *params):
        assert params is not None
        self.tasks.put(params)
        self.task_count += 1

    def map(self, *params):
        # todo
        assert params is not None
        self.tasks.put(params)

    def shutdown_now(self):
        """解决未执行任务发生异常可能导致线程池无法退出问题"""
        self.tasks.queue.clear()
        self.shutdown()

    def shutdown(self):
        """
        :return: exceptions -> [[task, e],]  相当于在提交的task后追加了异常e
        """
        self.task_retry()
        for _ in self.thread_list:
            self.tasks.put(None)
        for thread in self.thread_list:
            # self.tasks.put(None)  在此处放None会被其他线程抢走，进而导致卡死
            thread.join()
        self.is_running = False
        # exception -> (task, e)
        if self.print_exc:
            self.print_exceptions()
        return self.exceptions

    def task_retry(self):
        # 等待任务执行完后重试
        while not self.tasks.empty():
            sleep(2)
        if self.retry > 0 and len(self.exceptions) > 0:
            for _ in range(self.retry):
                exceptions = self.exceptions.copy()
                self.exceptions.clear()
                for exc in exceptions:
                    self.submit(*exc[:-1])

    def __enter__(self):
        # 此处self已经实例化，init时自动调用的
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 使用with语法不能返回异常
        if self.is_running:
            self.shutdown()

    def print_exceptions(self):
        print('exceptions:', self.exceptions)

    def set_monitor(self):
        """启动监视线程，需主动调用"""
        t.Thread(target=self.monitor).start()

    def monitor(self):
        # print会打断当前进度条，可以把print(…)语句改写为tqdm.write(…)，来防止这种情况的出现
        with tqdm(desc='线程池执行进度') as bar:
            pre_done = 0
            while self.is_running:
                bar.total = self.task_count
                done = self.task_count - self.tasks.qsize()
                bar.update(done - pre_done)
                pre_done = done
                sleep(2)


if __name__ == '__main__':
    pass
