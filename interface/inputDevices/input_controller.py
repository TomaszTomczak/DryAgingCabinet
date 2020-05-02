from threading import Thread, Event
from queue import Queue
import time
from abc import ABC, abstractmethod 

class InputEvent:
    def __init__(self, device_id, data):
        self.device_id = device_id
        self.data = data

class InputEventReceiver(ABC): #interface vor input event receivers
    @abstractmethod
    def onInputEvent(self, event : InputEvent):
        pass

class InputDevice(ABC):
    @abstractmethod
    def update(self, queue : Queue):
        pass

class InputDeviceFactory:
    @staticmethod
    def get(self, inputDeviceConfig):
        pass

class InputController:

    actions = Queue()
    eventReceivers = []
    inputDevices = []
    running = True

    def __init__(self, config):

        self.workerThread = Thread(target=self.update)
        self.eventThread = Thread(target=self.checkInputStatus)
        self.workerThread.setDaemon(True)
        self.checkThread.setDaemon(True)
        self.workerThread.start()
        self.eventThread.start()
        print("join worker")
        #self.workerThread.join()
        print("join checkThread")
        self.eventThread.join()
        print("all threads running")

    def register(self, client: InputEventReceiver):
        self.eventReceivers.append(client)

    def deregister(self, client: InputEventReceiver):
        self.eventReceivers.remove(client)

    def update(self):
        while self.running:
            for d in self.inputDevices:
                d.update(self.actions)
            time.sleep(0.001)
        
    def checkInputStatus(self):
        while self.running:
            while not self.actions.empty():
                data = self.actions.get()
                for receiver in self.eventReceivers:
                    receiver.onInputEvent(data)
            time.sleep(0.01)

if __name__ == '__main__':
    
    x = InputController("test")
    x.print()