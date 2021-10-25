from datetime import datetime, datetime as dt, timedelta, timedelta as delta
from enum import Enum
from typing import Optional


class _Status(Enum):
    RUNNING = 1
    STOPPED = 0


class CountDowner:
    """
    Count down the given time, and give signal/notification if time is up.
    """
    duration: timedelta
    _has_noti: bool
    _previous_update_time: Optional[datetime]
    _remaining_time: timedelta
    _run_status: _Status

    @property
    def remaining_time(self) -> delta:
        """auto updated"""
        self._update_time()
        return self._remaining_time

    def __init__(self, duration: delta = delta(hours=1),
                 direct_start=True,
                 remaining_time: Optional[delta] = None):
        assert duration.total_seconds() > 0
        self.duration = duration
        self._remaining_time = duration if remaining_time is None else \
            remaining_time
        assert self._remaining_time.total_seconds() > 0, \
            f"remaining_time={remaining_time!r} should be positive."

        self._run_status = _Status.STOPPED
        self._previous_update_time = None  # helper to update the counter

        self._has_noti = False
        self._direct_start = direct_start
        # DONE init

        if self._direct_start:
            self.start()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(duration={self.duration!r}, " \
               f"direct_start={self._direct_start!r}, " \
               f"remaining_time={self.remaining_time!r}, " \
               f"is_running={self.is_running()}, " \
               f"_has_noti={self._has_noti})"

    # not really useful to be honest
    # def get_setting(self) -> Dict[str, Union[delta, bool]]:
    #     """ only export sensible values """
    #     return {
    #         "duration": self.duration,
    #         "remaining_time": self.remaining_time,
    #         "direct_start": self._direct_start,
    #         "_has_noti": self._has_noti
    #     }

    def start(self) -> None:
        if self._run_status == _Status.RUNNING:
            return
        self._run_status = _Status.RUNNING
        self._previous_update_time = dt.now()

    # def time_is_up(self, call_update=True) -> bool:
    #     if call_update:
    #         self._update_time()
    #     return self._time_is_up()

    def _time_is_up(self) -> bool:
        return self._remaining_time.total_seconds() <= 0

    def _update_time(self) -> None:
        if self._run_status == _Status.STOPPED:
            return
        assert self._previous_update_time is not None
        time_passed = dt.now() - self._previous_update_time
        self._previous_update_time += time_passed
        is_previous_time_up = self._time_is_up()
        self._remaining_time -= time_passed
        if not is_previous_time_up and self._time_is_up():
            self._has_noti = True

    def stop(self) -> None:
        if self._run_status == _Status.STOPPED:
            return
        self._update_time()
        self._run_status = _Status.STOPPED
        self._previous_update_time = None

    def reset(self) -> None:
        """just convenient for usage only"""
        self.set()

    def set(self, duration: Optional[delta] = None) -> None:
        self.stop()
        if duration is not None:
            self.duration = duration
        self._remaining_time = self.duration
        self._has_noti = False
        if self._direct_start:
            self.start()

    def call_event_by_str(self, event_str: str):
        assert event_str in ["Start", "Stop", "Reset"]
        if event_str == 'Start':
            self.start()
        elif event_str == 'Stop':
            self.stop()
        elif event_str == 'Reset':
            self.reset()

    @staticmethod
    def fmtDelta(t: delta) -> str:
        """format to hh:mm:ss"""
        ts = t.total_seconds()
        tm, ss = divmod(abs(ts), 60)
        hh, mm = divmod(tm, 60)
        return f"{'-' if ts < 0 else ' '}{hh:02.0f}:{mm:02.0f}:{ss:02.0f}"

    def get_updates(self, call_update=True) -> (bool, str, float):
        """
        has_notification, time_str, seconds_left
        get formatted string and time in seconds
        """
        tmp = self.remaining_time if call_update else self._remaining_time
        return self._has_noti, self.fmtDelta(tmp), tmp.total_seconds()

    def done_and_turn_off_noti(self):
        """This function is to be called when noti has been dealt with"""
        assert self._has_noti
        self._has_noti = False

    def is_running(self) -> bool:
        return self._run_status == _Status.RUNNING
