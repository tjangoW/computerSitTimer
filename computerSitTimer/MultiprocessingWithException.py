import multiprocessing as mp
import traceback
from typing import Optional, Tuple


class ProcessWithException(mp.Process):
    """
    to be treated same as usual multiprocessing process, with
    p = Process(target=target, args=args)
    p.start()
    p.join()
    p.print_and_raise_if_has_exception()

    extended from stack overflow https://stackoverflow.com/a/33599967/11837276
    """
    _exception: Optional[Tuple[Exception, str]]

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
    def exception(self) -> Tuple[Exception, str]:
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception

    def print_and_raise_if_has_exception(self):
        if self.exception is None:
            return
        print("=" * 30 + "\n")
        print("=" * 30 + "\n")
        print("=" * 30 + "\n")
        print(self.exception[1])
        raise self.exception[0]
