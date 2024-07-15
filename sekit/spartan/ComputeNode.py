# -*- coding: utf-8 -*-
import time
from collections import OrderedDict
from multiprocessing import cpu_count
from queue import Empty, Queue
from subprocess import PIPE, Popen
from threading import Lock, Thread, current_thread


class ComputeNodeThread(Thread):
    def __init__(self, p_cn, timeout=1, name="Thread"):
        super().__init__(name=name)
        self.p_cn = p_cn
        self.timeout = timeout
        self._continue = True
        self.cmd = None

    def run(self):
        try:
            while self._continue:
                try:
                    self.cmd = self.p_cn.q_commands.get(timeout=self.timeout)
                    device = None
                    if len(self.p_cn.device_state) > 0:
                        # このタイミングでdevice_stateが変わる可能性あり
                        device_key, device = self.p_cn.allocate_device()
                        if device is not None:
                            self.cmd += " --{} {}".format(device_key, device)
                    proc = self.exe_command()
                    proc.wait()
                    self.cmd = None  # 実行完了後にNoneにして終わった合図
                    if device is not None:
                        self.p_cn.release_device(device)
                    # 同時実行ジョブ数に変更があった場合の処理
                    with self.p_cn.lock:
                        if len(self.p_cn.threads) > self.p_cn.n_jobs:
                            self.p_cn.threads.remove(current_thread())
                            self.reserve_killed()
                except Empty as e:
                    continue
        finally:
            # print(self.name + ' was killed.')
            pass

    def reserve_killed(self):
        self._continue = False

    def exe_command(self):
        return Popen(self.cmd, shell=True)


class ComputeNode:
    """localhost内で復数のプロセスを並列実行するためのクラス。"""

    def __init__(
        self,
        n_jobs=1,
        interval=1,
        device=None,
        device_key="_device",
        thread_name="localhost",
    ):
        # self.commands = commands
        self.n_jobs = n_jobs
        self.interval = interval
        device = [] if device is None else device
        self.device_state = OrderedDict([[d, 0] for d in device])
        self.device_key = device_key
        self.hostname = "localhost"
        self.thread_name = thread_name
        self.lock = Lock()
        self.threads = []

    @property
    def n_jobs(self):
        return self.__n_jobs

    @n_jobs.setter
    def n_jobs(self, n_jobs):
        self.__n_jobs = cpu_count() if n_jobs < 0 else n_jobs

    def _start_setup(self, commands):
        if type(commands) == Queue:
            # Queueならそれを入れる
            self.q_commands = commands
        elif hasattr(commands, "__iter__"):
            # QueueではくてイテレーションするならQueueを**新しく**作る
            self.q_commands = Queue()
            for c in commands:
                self.q_commands.put(c)
        else:
            raise TypeError("Queue型もしくはイテレーション型を入れてください")

    def _start_thread(self, index):
        thread_name = "{}_{}".format(self.thread_name, index)
        thread = ComputeNodeThread(p_cn=self, name=thread_name)
        thread.start()
        self.threads.append(thread)

    def start(self, commands):
        self._start_setup(commands)
        for i in range(self.n_jobs):
            self._start_thread(i)

    def check_continue(self):
        with self.lock:
            is_executing = any([t.cmd for t in self.threads])
            is_not_empty = self.q_commands.empty() is False
        return is_executing or is_not_empty

    def wait_all(self):
        while self.check_continue():
            time.sleep(self.interval)
            # queueの数が0になってかつ、すべてのThreadがqueueを待機していたら終了
            # queueを待機している=実行は終了しているから
        self.kill_all()

    def change_n_jobs(self, n_jobs):  # 途中でjobの数を変える時の処理
        with self.lock:
            self.n_jobs = n_jobs
            while len(self.threads) < self.n_jobs:
                self._start_thread(index=len(self.threads))

    def change_device_state(self, devices):
        with self.lock:
            tmp_device_state = OrderedDict([[d, 0] for d in devices])
            for g, v in self.device_state.items():
                if g in tmp_device_state:
                    tmp_device_state[g] = v
            self.device_state = tmp_device_state

    def allocate_device(self):
        allocated_device = None
        with self.lock:
            min_value = min(self.device_state.values())
            for device, v in self.device_state.items():
                if v == min_value:
                    allocated_device = device
                    break
            self.device_state[allocated_device] += 1
        # print('---', self.device_state)
        return self.device_key, allocated_device

    def release_device(self, device):
        with self.lock:
            if device in self.device_state:
                value = self.device_state[device] - 1
                self.device_state[device] = max(0, value)

    def kill_all(self):
        with self.lock:
            for th in self.threads:
                th.reserve_killed()
