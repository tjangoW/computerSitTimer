from datetime import timedelta, timedelta as delta
from enum import Enum
from typing import Any

from computerSitTimer.CountDowner import CountDowner


class TimerInterface:
    """
    A Ui-independent/free interface for the timer with all functionality.
    Then ui will just be representation of this core
    """
    _noti_state: 'TimerInterface._NotifyState'
    _timer: CountDowner

    class _NotifyState(Enum):
        """
        Generally could have used += 1 to transit from one to the other, but for clarity it is not used here.
        """
        no_noti = 0
        to_noti = 1
        has_noti_ed = 2

    def __init__(self, timer_time: timedelta, direct_start=True):
        self._timer = CountDowner(timer_time)
        self._noti_state = self._NotifyState.no_noti
        # Ui Setting
        self.direct_start = direct_start
        if self.direct_start:
            self.start()

    def get_full_duration(self):
        return self._timer.duration

    def start(self) -> None:
        self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def reset(self) -> None:
        self.reset()
        self._noti_state = self._NotifyState.no_noti
        if self.direct_start:
            self.start()

    def set(self, duration: timedelta) -> None:
        self._timer.set(duration)
        if self.direct_start:
            self.start()

    def changeEvents(self, eventStr: str) -> None:
        assert (eventStr in ["Start", "Stop", "Reset"])
        if eventStr == 'Start':
            self.start()
        elif eventStr == 'Stop':
            self.stop()
        elif eventStr == 'Reset':
            self.reset()

    def updateTime(self) -> (bool, str, float):
        """
        :return: to_notify: whether notification should occur?
                 time_str: formatted str of current time
                 seconds_left: seconds left till time is up
        """
        time_str, seconds_left = self._timer.get_time()
        to_notify = (seconds_left < 0) and (self._noti_state == self._NotifyState.no_noti)
        if to_notify:
            self._noti_state = self._NotifyState.to_noti

        return to_notify, time_str, seconds_left

    def toNotify(self, call_update=True) -> bool:
        if call_update:
            self.updateTime()
        return self._noti_state == self._NotifyState.to_noti

    def offToNotifyState(self) -> None:
        """ This function is to be called when notification has been dealt with """
        if self._noti_state != self._NotifyState.to_noti:
            raise Exception("Something wrong with the code! call to offToNotifyState should not occur here.")
        self._noti_state = self._NotifyState.has_noti_ed

    def is_running(self) -> bool:
        return self._timer.is_running()


if __name__ == '__main__':
    c = TimerInterface(delta(seconds=5))
