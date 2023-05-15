import datetime
import logging
import subprocess
from datetime import timedelta
from pathlib import Path
from typing import List, Optional

import PySimpleGUIQt as sg
from PySimpleGUIQt import SystemTray, Window

from computerSitTimer.CountDowner import CountDowner
from computerSitTimer.media.MediaHelper import get_icon_path

logging.warning(sg.version)
logging.warning(sg.sys.version)

sg.theme('DarkTanBlue')  # Add a touch of color


class Event:
    SHOW_POPUP = "Show Popup"


class EndTime:
    hour: int
    minute: int

    def __init__(self, hour: int = 23, minute: int = 30):
        self.hour = hour
        self.minute = minute

    def as_datetime(self):
        now = datetime.datetime.now()
        end_time = now.replace(hour=self.hour, minute=self.minute, second=0, microsecond=0)
        if end_time < now:
            end_time += timedelta(days=1)
        return end_time

    def get_delta_from_now(self) -> timedelta:
        return self.as_datetime() - datetime.datetime.now()

    def as_str(self):
        return self.as_datetime().strftime("%H:%M")


class EndTimer:
    """Using composition as many of CountDowner features are not desirable."""
    _timer: CountDowner
    end_time: EndTime
    extra_time_minutes: float

    def __init__(self, hour: int = 23, minute: int = 30, extra_time_minutes: float = 5):
        self.end_time = EndTime(hour, minute)
        self._timer = CountDowner(self.end_time.get_delta_from_now())
        assert extra_time_minutes >= 0
        self.extra_time_minutes = extra_time_minutes

    def reset(self) -> None:
        self._timer.set(self.end_time.get_delta_from_now())

    def get_updates(self):
        to_notify, time_str, seconds_left = self._timer.get_updates()
        if seconds_left <= - self.extra_time_minutes * 60:
            self.reset()
            to_notify, time_str, seconds_left = self._timer.get_updates()
            subprocess.call(Path.home() / "Desktop/hibernate.cmd")

        if to_notify:
            self._timer.done_and_turn_off_noti()
        return to_notify, time_str, seconds_left


class Const:
    """
    A namespace instead of a class to have all constants
    """
    TIMEOUT_POPUP = 333  # in milliseconds
    TIMEOUT_TRAY = 1000  # in milliseconds


class PopUp:
    _timer: EndTimer
    _window: Optional[Window]

    _currentTimeKey = '_time_'
    _durationKey = "_duration_"
    _msgKey = '_msg_'
    durationFormat = "mm, mm:ss or hh:mm:ss"
    font = 'Helvetica'
    negativeFontColor = '#df0000'
    normalFontColor: str

    def __init__(self, timer: EndTimer):
        self._timer = timer
        self.keepOnTop = True
        self.start_minimised = True
        self._window = None

    def create_window(self):
        layout = [[sg.Text('', key=self._msgKey, # size=(30, 1),
                           auto_size_text=True, font=(self.font, 15),
                           justification='center')],
                  [sg.Text(f'Time left till {self._timer.end_time.as_str()}: '),
                   sg.Text('', key=self._currentTimeKey, size=(20, 1))],
                  ]

        self._window = Window(title='Pc Sleep Timer', layout=layout,
                              keep_on_top=self.keepOnTop,
                              # enable_close_attempted_event=True,
                              icon=get_icon_path(True))
        self.normalFontColor = self._window[self._currentTimeKey].TextColor

    def _update_time(self):
        to_notify, time_str, seconds_left = self._timer.get_updates()
        logging.debug(f"-- UI update: {time_str}")
        self._window[self._currentTimeKey].Update(time_str, text_color=(
            self.normalFontColor if seconds_left >= 0 else
            self.negativeFontColor))
        if seconds_left < 0 and len(self._window[self._msgKey].DisplayText) == 0:
            self._window[self._msgKey].Update(f"Time's up! PC off in {self._timer.extra_time_minutes} minutes...")

    def run(self) -> None:
        self.create_window()
        # Event loop
        while True:
            event, values = self._window.Read(timeout=Const.TIMEOUT_POPUP)

            if event in (sg.WIN_CLOSED,):
                self._window.close()
                break
            # elif event in (sg.WIN_CLOSE_ATTEMPTED_EVENT,):
            #     # disable closing using Alt+F4 or the close button
            #     pass
            elif event in [sg.EVENT_TIMEOUT]:
                pass
            else:
                pass

            self._update_time()


class MainTray:
    """
    The Main class, basically the tray object.
    So now tray will be the master, and when time is up, it will make a
    (blocking) call to show the UI.
    Tray will run at all time while PopUp is not required.
    """
    _timer: EndTimer
    _tray: Optional[SystemTray]
    _icon_is_running: bool

    def __init__(self, end_timer: EndTimer):
        self._timer = end_timer
        self._tray = None  # none as multiprocessing cannot pickle QT object

    def _create_tray(self):
        self._tray = SystemTray()
        self._update_tray_all()

    @staticmethod
    def _create_menu_list() -> List[List[str]]:
        """ A specific function so that sound option can be set accordingly
            Don't try to put time here, it will keep changing and the menu
            will just disappear.
        """
        menu_def = ['UNUSED', [Event.SHOW_POPUP]]
        return menu_def

    def run(self):
        self._create_tray()
        """running the main loop"""
        while True:
            event = self._tray.Read(timeout=Const.TIMEOUT_TRAY)

            if event in (sg.EVENT_TIMEOUT,
                         sg.EVENT_SYSTEM_TRAY_ICON_ACTIVATED):
                pass
            elif event in (Event.SHOW_POPUP,
                           sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
                self._show_popup()
            else:
                logging.debug(event.__repr__())
                raise RuntimeError(f"Unhandled event: {event!r}")

            self._update_time()

    def _show_popup(self):
        PopUp(self._timer).run()

    def _update_time(self):
        has_noti, time_str, _ = self._timer.get_updates()
        self._update_tray(time_str)
        if has_noti:
            logging.debug(f"-- tray update: {time_str}")
            self._tray.ShowMessage("Time is up!", "Go to sleep!")
            logging.debug("tray calling UI as time's up")
            self._show_popup()

    def _update_tray_all(self):
        self._update_tray(update_time=True)

    def _update_tray(self, time_str: Optional[str] = None, update_time=False) -> None:
        """Update menu, tray icon etc"""

        update_kwargs = {}
        if time_str is not None:
            update_kwargs.update(tooltip=time_str)
        elif update_time:
            update_kwargs.update(
                tooltip=self._timer.get_updates()[1])
        self._tray.update(**update_kwargs)


if __name__ == '__main__':
    test = False
    if test:
        nw = datetime.datetime.now()
        et = EndTimer(nw.hour, nw.minute + 1)
    else:

        et = EndTimer(hour=23, minute=30, extra_time_minutes=15)
    MainTray(et).run()
    # sg.preview_all_look_and_feel_themes()
