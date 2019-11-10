import threading
import time

class Th:

    def __init__(self):
        self.val = 6

        self.keep_alive = threading.Thread(name='keep_alive', target=self.blah, args=())
        self.val = 5

        self.keep_alive.setDaemon(True)
        self.keep_alive.start()

        print("PAST THREAD INIT")

        while True:
            self.val -= 1
            time.sleep(1)

    def blah(self):

        while True:
            print(self.val)
            time.sleep(1)


t = Th()