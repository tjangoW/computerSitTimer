from datetime import timedelta as delta, timedelta
from datetime import datetime as dt, datetime
from enum import Enum
from typing import Optional, Dict, Union


class CountDowner:
    duration: timedelta
    _status: 'CountDowner._Status'
    _remaining_time: timedelta
    _previous_update_time: Optional[datetime]

    @property
    def remaining_time(self) -> delta:
        """auto updated"""
        self._update_time()
        return self._remaining_time

    class _Status(Enum):
        RUNNING = 1
        STOPPED = 0

    def __init__(self, duration: delta = delta(hours=1), remaining_time: Optional[delta] = None,
                 is_running: bool = False):
        self.duration = duration
        self._remaining_time = duration if remaining_time is None else remaining_time
        self._status = self._Status.STOPPED
        self._previous_update_time = None  # helper variable to update the counter
        if is_running:
            self.start()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(duration={self.duration!r}, " \
               f"remaining_time={self.remaining_time!r}, " \
               f"is_running={self.is_running()})"

    def get_setting(self) -> Dict[str, Union[delta, bool]]:
        """ Output from this should be usable for 'createFromString'! """
        return {
            "duration": self.duration,
            "remaining_time": self.remaining_time,
            "is_running": self.is_running()
        }

    def start(self) -> None:
        if self._status == self._Status.RUNNING:
            return
        self._status = self._Status.RUNNING
        self._previous_update_time = dt.now()

    def _update_time(self) -> None:
        if self._status == self._Status.STOPPED:
            return
        assert self._previous_update_time is not None
        time_passed = dt.now() - self._previous_update_time
        self._remaining_time -= time_passed
        self._previous_update_time += time_passed

    def stop(self) -> None:
        if self._status == self._Status.STOPPED:
            return
        self._update_time()
        self._status = self._Status.STOPPED
        self._previous_update_time = None

    def set(self, duration: delta) -> None:
        self._set(duration)

    def reset(self) -> None:
        self._set()

    def _set(self, duration: Optional[delta] = None) -> None:
        self.stop()
        if duration is not None:
            self.duration = duration
        self._remaining_time = self.duration

    @staticmethod
    def fmtDelta(t: delta) -> str:
        """format to hh:mm:ss"""
        ts = t.total_seconds()
        tm, ss = divmod(abs(ts), 60)
        hh, mm = divmod(tm, 60)
        return f"{'-' if ts < 0 else ' '}{hh:02.0f}:{mm:02.0f}:{ss:02.0f}"

    def get_time(self, call_update_time=True) -> (str, float):
        """get formatted string and time in seconds"""
        tmp = self.remaining_time if call_update_time else self._remaining_time
        return self.fmtDelta(tmp), tmp.total_seconds()

    def is_running(self) -> bool:
        return self._status == self._Status.RUNNING

    def is_stopped(self) -> bool:
        return self._status == self._Status.STOPPED
