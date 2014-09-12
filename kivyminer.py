#!/usr/bin/env python
from subprocess import PIPE, Popen, STDOUT
from threading import Thread
from Queue import Queue, Empty
from os import system
from re import sub
import sys
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label


def read_output(process, stdout, queue):
    while True:
        out = stdout.readline()
        if out == '' and process.poll() != None:
            break
        if out != '':
            line = out.rstrip()
            queue.put_nowait(line)
            sys.stdout.flush()


class RootWidget(BoxLayout):
    """Root Kivy box layout class"""
    threadInput = ObjectProperty()
    urlInput = ObjectProperty()
    userAddress = ObjectProperty()
    outputLabel = ObjectProperty()
    hashrateLabel = ObjectProperty()
    p = None
    q = Queue()
    minerdOutput = ['...', '...', '...', '...', '...']
    nThreads = 0

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)

    def start_miner(self):
        try:
            if int(self.threadInput.text) <= 32:
                self.nThreads = float(self.threadInput.text)
                self.p = Popen(["QubitCPU32.exe", "-a", "qubit",
                            "-t", self.threadInput.text, "-o", self.urlInput.text,
                            "-u", self.userAddress.text, "-p", "x"],
                            stdout=PIPE,
                            stderr=STDOUT,
                            bufsize=1)
                t = Thread(target=read_output, args=(self.p, self.p.stdout, self.q))
                t.daemon = True  # thread dies with the program
                t.start()
                Clock.schedule_interval(self.read_queue, 0.1)
            else:
                popup = Popup(title='Too Many Threads Popup',
                content=Label(text='Please choose a value <= 32.'),
                size_hint=(0.7, 0.7))
                popup.open()
        except ValueError:
            popup = Popup(title='Not An Integer Popup',
            content=Label(text='Please enter an integer <= 32.'),
            size_hint=(0.7, 0.7))
            popup.open()


    def stop_miner(self):
        system("taskkill /im QubitCPU32.exe /f")
        self.p.kill()
        self.outputLabel.text = ''
        self.hashrateLabel.text = '0.0 khash/s'
        # exit(0)

    def read_queue(self, dt):
        try:
            newLine = self.q.get_nowait()
            if 'khash' in newLine:
                hashrate = float(sub("[^0123456789\.]","",newLine.split(',')[1]))
                self.hashrateLabel.text = str(hashrate*self.nThreads) + " khash/s"
            self.minerdOutput.pop(0)
            self.minerdOutput.append(newLine)
            outputText = ''
            for line in self.minerdOutput:
                outputText = outputText + line + '\n'
            # print outputText
            self.outputLabel.text = outputText
        except Empty:
            pass


class KivyMiner(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    Config.set('kivy', 'exit_on_escape', 0)
    KivyMiner().run()
    try:
        system("taskkill /im QubitCPU32.exe /f")
    except:
        pass