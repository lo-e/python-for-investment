# -- coding: utf-8 --

from threading import Thread
from time import sleep

class testClass(object):
    def __init__(self, interval:int):
        self.interval = interval
        self.timer1 = Thread(target=self.on_timer1)
        self.timer2 = Thread(target=self.on_timer2)

    def start(self):
        self.timer1.start()
        self.timer2.start()

    def on_timer1(self):
        while True:
            print('timer_1 waiting..')
            sleep(self.interval)
            print('timer_1 open\n')

    def on_timer2(self):
        while True:
            sleep(1)
            print('timer_2')

if __name__ == '__main__':
    test = testClass(interval=6)
    test.start()


