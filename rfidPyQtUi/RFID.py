import serial
from threading import Thread

class RFID():
    def __init__(self):
        self.ser = serial

    def start(self):
        print("Start serial")

    def stop(self):
        print("Stop connection")

    def checkPort(self):
        print("Check port")