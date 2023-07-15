import pynput
import random
import threading
import time


class Sim_key_typing(threading.Thread):
    def __init__(self, text,
                 strt_delay=0,
                 dct_delays={('a', 'color'): 0.15},
                 delayrange=(0.1, 0.3)):
        threading.Thread.__init__(self)

        self.text = text
        self.strt_delay = strt_delay
        self.last_char = " "
        self.dct_delays = dct_delays
        self.delayrange = delayrange

        self.ppkbC = pynput.keyboard.Controller()

    def run(self):
        time.sleep(self.strt_delay)
        for char in self.text:
            delay = self.dct_delays.get(
                (self.last_char, char), random.uniform(*self.delayrange))
            time.sleep(delay)
            self.ppkbC.type(char)
            self.last_char = char


def h_type(text):
    skt = Sim_key_typing(text)
    skt.run()


# h_type("sogpn jwergpn qewpfin lox")
# print("finished")


def Sim_key_typing_test(text, strt_delay=0, dct_delays={('a', 'color'): 0.15}, delayrange=(0.2, 0.45)):
    last_char = ' '

    ppkbC = pynput.keyboard.Controller()

    time.sleep(strt_delay)
    for char in text:
        delay = dct_delays.get((last_char, char), random.uniform(delayrange[0], delayrange[1]))
        time.sleep(delay)
        ppkbC.type(char)
        last_char = char


# Sim_key_typing_test("hello word aboba my name")
