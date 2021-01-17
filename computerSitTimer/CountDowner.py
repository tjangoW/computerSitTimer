from datetime import timedelta as delta, timedelta
from datetime import datetime as dt, datetime
from enum import Enum
from typing import Optional, Dict, Union


class CountDowner:
    duration: timedelta
    status: 'CountDowner._Status'
    _remaining_time: timedelta
    _previous_update_time: Optional[datetime]

    class _Status(Enum):
        RUNNING = 1
        STOPPED = 0

    def __init__(self, duration: delta = delta(hours=1)):
        self.duration = duration
        self._remaining_time = duration
        self.status = self._Status.STOPPED
        self._previous_update_time = None  # helper variable to update the counter

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} ({'RUNNING' if self.is_running() else 'STOPPED'}), "\
               f"Duration={self.fmtDelta(self.duration)}, " \
               f"left={self.fmtDelta(self.remaining_time)}"

    def getSetting(self) -> Dict[str, Union[delta, bool]]:
        """ Output from this should be usable for 'createFromString'! """
        return {
            "duration": self.duration,
            "remaining_time": self.remaining_time,
            "is_running": self.is_running()
        }

    @classmethod
    def createFromSetting(cls, duration: delta, remaining_time: delta, is_running: bool) -> "CountDowner":
        inst = cls(duration)
        if is_running:
            inst.start()
        if duration != remaining_time:
            inst._remaining_time = remaining_time
        return inst

    def start(self) -> None:
        if self.status == self._Status.RUNNING:
            return
        self.status = self._Status.RUNNING
        self._previous_update_time = dt.now()

    def _update_time(self) -> None:
        if self.status == self._Status.STOPPED:
            return
        time_passed = dt.now() - self._previous_update_time
        self._remaining_time -= time_passed
        self._previous_update_time += time_passed

    def stop(self) -> None:
        if self.status == self._Status.STOPPED:
            return
        self._update_time()
        self.status = self._Status.STOPPED
        self._previous_update_time = None

    def set(self, duration: delta) -> None:
        self._reset(duration)

    def reset(self) -> None:
        self._reset()

    def _reset(self, duration: Optional[delta] = None) -> None:
        self.stop()
        if duration is not None:
            self.duration = duration
        self._remaining_time = self.duration

    @staticmethod
    def fmtDelta(t: delta) -> str:
        ts = t.total_seconds()
        tm, ss = divmod(abs(ts), 60)
        hh, mm = divmod(tm, 60)
        return f"{'-' if ts < 0 else ' '}{hh:02.0f}:{mm:02.0f}:{ss:02.0f}"

    def get_time(self, call_update_time=True) -> (str, float):
        """get formatted string and time in seconds"""
        if call_update_time:
            self._update_time()
        return self.fmtDelta(self._remaining_time), self._remaining_time.total_seconds()

    @property
    def remaining_time(self) -> delta:
        self._update_time()
        return self._remaining_time

    def is_running(self) -> bool:
        return self.status == self._Status.RUNNING

    def is_stopped(self) -> bool:
        return self.status == self._Status.STOPPED


if __name__ == '__main__':
    c = CountDowner(delta(seconds=5))
    print(c)
    c.start()
    print(c)

    from time import sleep

    print("---- pause in between")
    sleep(3)
    print(c)
    c.stop()
    print(c)
    c.start()
    print(c)

    print("---- over time")
    sleep(5)
    print(c)
    c.start()
    print(c)
    c.stop()
    print(c)

    print("---- Resetting")
    c.reset()
    print(c)

    c.start()
    print(c)
    sleep(5)
    print("---- time up!")
    print(c)
    c.stop()
    print(c)
