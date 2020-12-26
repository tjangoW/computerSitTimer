from enum import Enum
from typing import Optional, Final, Any
from datetime import timedelta as delta, timedelta

from computerSitTimer.AudioPlayer import AudioPlayer
from computerSitTimer.CountDowner import CountDowner


class CoreBI:
    """
    An Ui-independent interface for the timer with all functionality.
    Then ui will just be representation of this core
    """
    start_minimised: bool
    keepOnTop: bool
    noti_player: AudioPlayer
    _noti_state: 'CoreBI._NotifyState'
    _timer: CountDowner

    class _NotifyState(Enum):
        """
        Generally could have used += 1 to transit from one to the other, but for clarity it is not used here.
        """
        no_noti: Final = 0
        to_noti: Final = 1
        has_noti_ed: Final = 2

    def __init__(self, timer_time: timedelta, sound_on: bool = False, sound_file: Optional[str] = None):
        self._timer = CountDowner(timer_time)
        self.noti_player = AudioPlayer(sound_file, sound_on)
        self._noti_state = self._NotifyState.no_noti
        # Ui Setting
        self.keepOnTop = True
        self.start_minimised = True
        self.direct_start = True

        # direct start
        if self.direct_start:
            self.start()

    def getSetting(self, key: str) -> Any:
        settings = self.getSettings()
        assert(key in settings), f"Invalid key ({key}) for setting!"
        return settings[key]

    def getSettings(self):
        return {
            "timer_time": self._timer.duration,  # no point of resuming exact state of timer, so only duration
            "sound_on": self.noti_player.is_sound_on,
            "sound_file": self.noti_player.wav_filename,
            "keepOnTop": self.keepOnTop
        }

    def start(self) -> None:
        self.changeEvents("Start")

    def stop(self) -> None:
        self.changeEvents("Stop")

    def reset(self) -> None:
        self.changeEvents("Reset")

    def set(self, duration: timedelta) -> None:
        self._timer.set(duration)
        if self.direct_start:
            self.start()

    def changeEvents(self, eventStr: str) -> None:
        assert (eventStr in ["Start", "Stop", "Reset"])
        if eventStr == 'Start':
            self._timer.start()
        elif eventStr == 'Stop':
            self._timer.stop()
            self.noti_player.stop()
        elif eventStr == 'Reset':
            self.noti_player.stop()
            self._timer.reset()
            self._noti_state = self._NotifyState.no_noti
            if self.direct_start:
                self.start()

    def updateTime(self) -> (bool, str, float):
        """
        :return: to_notify: whether notification should occur?
                 time_str: formatted str of current time
                 seconds_left: seconds left till time is up
        """
        time_str, seconds_left = self._timer.get_time()
        to_notify: Final = (seconds_left < 0) and (self._noti_state == self._NotifyState.no_noti)
        if to_notify:
            self._noti_state = self._NotifyState.to_noti
            self.noti_player.play()

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
    c = CoreBI(delta(seconds=5))
