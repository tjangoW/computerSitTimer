import datetime
import logging
import multiprocessing as mp
import sys
from datetime import timedelta

from computerSitTimer.Ui import MainTray

import traceback


class Process(mp.Process):
    """from stack overflow https://stackoverflow.com/a/33599967/11837276"""
    def __init__(self, *args, **kwargs):
        mp.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            mp.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            # raise e  # You can still rise this exception if you need to

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception


def run_ability_check_of_not_ending_function(target, args, timeout):
    """check if a function can run without error within the given timeout"""
    p = Process(target=target, args=args)
    p.start()

    print(datetime.datetime.now())
    p.join(timeout)
    print(datetime.datetime.now())
    exception = p.exception
    if exception is not None:
        print(exception[1])
        print("="*30 + "\n")
        print("="*30 + "\n")
        print("="*30 + "\n")
        raise exception[0]("See traceback print above.")
    p.kill()
    p.terminate()
    p.join()
    print(datetime.datetime.now())


def test_tray_run():
    """just to make sure it can run """
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    m = MainTray(timedelta(seconds=2))
    run_ability_check_of_not_ending_function(target=m.run, args=(), timeout=5)
    pass
