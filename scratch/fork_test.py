import os

def child():
    print 'Hello from child' +str(os.getpid())
    os._exit(0)

def parent():
    while True:
        newpid = os.fork()
        if newpid == 0:
            child()
        else:
            print  'hello from parent' + str(os.getpid()) + str(newpid)
        if raw_input() == 'q':
            break

parent()
