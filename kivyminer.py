#!/usr/bin/env python
from subprocess import PIPE, Popen
from threading import Thread
from Queue import Queue, Empty
from os import system
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.clock import Clock


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


class RootWidget(BoxLayout):
    """Root Kivy box layout class"""
    threadInput = ObjectProperty()
    urlInput = ObjectProperty()
    userAddress = ObjectProperty()
    outputLabel = ObjectProperty()
    p = None
    q = Queue()

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)


    def start_miner(self):
        self.p = Popen(["QubitCPU32.exe", "-a", "qubit",
                    "-t", self.threadInput.text, "-o", self.urlInput.text,
                    "-u", self.userAddress.text, "-p", "x"],
                    stdout=PIPE,
                    stdin=PIPE,
                    bufsize=1)

        t = Thread(target=enqueue_output, args=(self.p.stdout, self.q))
        t.daemon = True  # thread dies with the program
        t.start()
        Clock.schedule_interval(self.read_queue, 0.1)

    def stop_miner(self):
        system("taskkill /im QubitCPU32.exe /f")
        # exit(0)

    def read_queue(self, dt):
        try:
            line = self.q.get_nowait()
            print line+line
            self.outputLabel.text = line
        except Empty:
            pass


class KivyMiner(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    Config.set('kivy', 'exit_on_escape', 0)
    KivyMiner().run()
    system("taskkill /im QubitCPU32.exe /f")
