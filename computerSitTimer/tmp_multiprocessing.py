import os
from multiprocessing import Process
from time import sleep


def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())


def f(name):
    info('function f')
    print('--> hello', name)
    sleep(10)
    print('--> end hello', name)


def _main1_info():
    info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()
    pass


import multiprocessing as mp


def foo(q):
    q.put('hello')


def _main2_mp():
    ctx = mp.get_context('spawn')
    q = ctx.Queue()
    p = ctx.Process(target=foo, args=(q,))
    p.start()
    print(q.get())
    p.join()
    pass


from multiprocessing import Process, Lock


def f_lock(lock, i):
    lock.acquire()
    try:
        print('hello world', i)
    finally:
        lock.release()
        pass


def _main3_lock():
    lock = Lock()

    for num in range(10):
        Process(target=f_lock, args=(lock, num)).start()


if __name__ == '__main__':
    # _main1_info()
    # _main2_mp()
    _main3_lock()
