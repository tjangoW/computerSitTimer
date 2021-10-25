import datetime
import multiprocessing as mp
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
    """check if a function can run without error within the given timeout.
        There are possibly better solutions like some decorators out there i guess?
    """
    p = Process(target=target, args=args)
    p.start()

    print(datetime.datetime.now())
    p.join(timeout)
    print(datetime.datetime.now())
    exception = p.exception
    if exception is not None:
        print(exception[1])
        print("=" * 30 + "\n")
        print("=" * 30 + "\n")
        print("=" * 30 + "\n")
        raise exception[0]("See traceback print above.")
    # p.kill()  # no kill in 3.6
    p.terminate()
    p.join()
    print(datetime.datetime.now())
