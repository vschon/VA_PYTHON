import threading
import datetime as dt

class test_thread(threading.Thread):
    def __init(self):
        threading.Thread.__init__(self)
        self.load = 0

    def run(self):
        while True:
            self.load = 1
            tt = dt.datetime.now()
            if tt > dt.datetime(2013,11,13,18,50):
                break
        print '\n finished backgorund job'


test = test_thread()
test.start()
print 'the main program continues to run in foreground'

test.join()
print ' main program waits until the background was done'
