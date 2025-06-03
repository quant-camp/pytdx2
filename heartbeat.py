# coding=utf-8

from threading import Thread
from log import log
import time

# 参考 :https://stackoverflow.com/questions/6524459/stopping-a-thread-after-a-certain-amount-of-time


DEFAULT_HEARTBEAT_INTERVAL = 15.0 # 15秒一个heartbeat

class HeartBeatThread(Thread):

    def __init__(self, client, stop_event, heartbeat, heartbeat_interval=DEFAULT_HEARTBEAT_INTERVAL):
        self.client = client
        self.stop_event = stop_event
        self.heartbeat = heartbeat
        self.heartbeat_interval = heartbeat_interval
        super(HeartBeatThread, self).__init__()
        self.last_ack_time = time.time()
    
    def update_last_ack_time(self):
        self.last_ack_time = time.time()

    def run(self):
        while not self.stop_event.is_set():
            self.stop_event.wait(self.heartbeat_interval)
            if self.client and (time.time() - self.last_ack_time > self.heartbeat_interval):
                try:
                    # 发送一个获取股票数量的包作为心跳包
                    self.heartbeat()
                except Exception as e:
                    log.debug(str(e))


