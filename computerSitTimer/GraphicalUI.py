import logging
from datetime import timedelta
from typing import List, Optional

import PySimpleGUIQt as sg
from PySimpleGUIQt import SystemTray, Window

from computerSitTimer.CountDowner import CountDowner
from computerSitTimer.media.MediaHelper import get_icon_path

logging.warning(sg.version)
logging.warning(sg.sys.version)

sg.theme('DarkTanBlue')  # Add a touch of color


class Event:
    """all should have the same name"""
    START = "Start"
    STOP = "Stop"
    RESET = "Reset"
    SET = "Set"
    EXIT = "Exit"
    SHOW_POPUP = "Show Popup"
    CLOSE_POPUP = "Close"


class Const:
    """
    A namespace instead of a class to have all constants
    """
    TIMEOUT_POPUP = 333  # in milliseconds
    TIMEOUT_TRAY = 1000  # in milliseconds


class PopUp:
    _timer: CountDowner
    _window: Optional[Window]

    _currentTimeKey = '_time_'
    _durationKey = "_duration_"
    _msgKey = '_msg_'
    durationFormat = "mm, mm:ss or hh:mm:ss"
    font = 'Helvetica'
    negativeFontColor = '#df0000'
    normalFontColor: str

    def __init__(self, timer: CountDowner):
        self._timer = timer
        self.keepOnTop = True
        self.start_minimised = True
        self._window = None

    def create_window(self):
        layout = [[sg.Text('', key=self._msgKey, size=(20, 1),
                           auto_size_text=True, font=(self.font, 20),
                           justification='center')],
                  [sg.Text('Current time: '),
                   sg.Text('', key=self._currentTimeKey, size=(20, 1))],
                  [sg.Text('Full time: '),
                   sg.Input(self._timer.duration, key=self._durationKey,
                            tooltip=f"in the format {self.durationFormat}",
                            enable_events=True),
                   sg.Button(Event.SET, button_color=('white', '#FF8800'),
                             bind_return_key=True)],
                  [sg.Button(Event.START, button_color=('white', '#00FF00')),
                   sg.Button(Event.STOP, button_color=('white', '#FF0000')),
                   sg.Button(Event.RESET, button_color=('white', '#FF8800'))],
                  [sg.Quit(Event.CLOSE_POPUP)]]

        self._window = Window(title='Simple Clock', layout=layout,
                              keep_on_top=self.keepOnTop,
                              icon=get_icon_path(True))
        self.normalFontColor = self._window[self._currentTimeKey].TextColor

    def _update_time(self):
        to_notify, time_str, seconds_left = self._timer.get_updates()
        logging.debug(f"-- UI update: {time_str}")
        self._window[self._currentTimeKey].Update(time_str, text_color=(
            self.normalFontColor if seconds_left >= 0 else
            self.negativeFontColor))
        if to_notify:
            self._timer.done_and_turn_off_noti()
        if seconds_left < 0 and len(self._window[self._msgKey].DisplayText) == 0:
            self._window[self._msgKey].Update("Time's up!")

    def run(self) -> None:
        self.create_window()
        # Event loop
        while True:
            event, values = self._window.Read(timeout=Const.TIMEOUT_POPUP)

            # Exits program cleanly if user clicks "X" or Event.CLOSE_POPUP
            # buttons
            if event in (sg.WIN_CLOSED, Event.CLOSE_POPUP):
                seconds_left = self._timer.get_updates()[2]
                if seconds_left < 0:
                    self._timer.reset()
                self._window.close()
                break
            elif event in [Event.START, Event.STOP, Event.RESET]:
                self._timer.call_event_by_str(event)
                if event == Event.RESET:
                    self._window[self._msgKey].Update('')
            elif event in [Event.SET]:
                self._parse_input_time_n_set()
            elif event in [sg.EVENT_TIMEOUT]:
                pass
            else:
                pass

            self._update_time()

    def _parse_input_time_n_set(self) -> None:
        edit = self._window[self._durationKey]
        duration_str: List[str] = edit.Get().split(":")

        if len(duration_str) not in [1, 2, 3]:
            self._show_invalid_format_popup()
            return

        if len(duration_str) == 2:
            duration_str.insert(0, "0")
        elif len(duration_str) == 1:
            duration_str = ["0", duration_str[0], "0"]
        try:
            duration = [int(i) for i in duration_str]
            self._timer.set(timedelta(hours=duration[0], minutes=duration[1],
                                      seconds=duration[2]))
        except ValueError:
            self._show_invalid_format_popup()

    def _show_invalid_format_popup(self):
        sg.Popup(f"Invalid duration format! It must be in the form of"
                 f" {self.durationFormat}.", keep_on_top=True)


class MainTray:
    """
    The Main class, basically the tray object.
    So now tray will be the master, and when time is up, it will make a
    (blocking) call to show the UI.
    Tray will run at all time while PopUp is not required.
    """
    _timer: CountDowner
    _tray: Optional[SystemTray]
    _icon_is_running: bool

    def __init__(self, delta: timedelta):
        self._timer = CountDowner(delta)
        self._tray = None  # none as multiprocessing cannot pickle QT object
        self._icon_is_running = self._timer.is_running()

    def _create_tray(self):
        self._tray = SystemTray()
        self._update_tray_all()

    @staticmethod
    def _create_menu_list() -> List[List[str]]:
        """ A specific function so that sound option can be set accordingly
            Don't try to put time here, it will keep changing and the menu
            will just disappear.
        """
        menu_def = ['UNUSED', [Event.START, Event.STOP, Event.RESET, "---",
                               Event.SHOW_POPUP, "---",
                               Event.EXIT]]
        return menu_def

    def run(self):
        self._create_tray()
        """running the main loop"""
        while True:
            event = self._tray.Read(timeout=Const.TIMEOUT_TRAY)

            # Exits program cleanly if user clicks "X" or "Quit" buttons
            if event == Event.EXIT:
                self._tray.close()
                break
            elif event in [Event.START, Event.STOP, Event.RESET]:
                self._timer.call_event_by_str(event)
                self._update_tray_all()
                continue
            elif event in (sg.EVENT_TIMEOUT,
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
        self._additional_icon_check_and_update()
        has_noti, time_str, _ = self._timer.get_updates()
        self._update_tray(time_str)
        if has_noti:
            logging.debug(f"-- tray update: {time_str}")
            self._tray.ShowMessage("Time is up!",
                                  "Move your ass away from the chair please!")
            logging.debug("tray calling UI as time's up")
            self._timer.done_and_turn_off_noti()
            self._show_popup()

    def _update_tray_all(self):
        self._update_tray(update_menu=True, update_icon=True, update_time=True)

    def _update_tray(self, time_str: Optional[str] = None, update_time=False,
                     update_icon=False, update_menu=False) -> None:
        """Update menu, tray icon etc"""

        update_kwargs = {}
        if time_str is not None:
            update_kwargs.update(tooltip=time_str)
        elif update_time:
            update_kwargs.update(
                tooltip=self._timer.get_updates()[1])
        if update_icon:
            update_kwargs.update(
                filename=get_icon_path(self._timer.is_running()))
            self._additional_icon_check_and_update(False)
        if update_menu:
            update_kwargs.update(menu=self._create_menu_list())
        self._tray.update(**update_kwargs)

    def _additional_icon_check_and_update(self, check=True):
        """check if the current timer icon fits with the timer state"""
        prev_v = self._icon_is_running
        self._icon_is_running = self._timer.is_running()

        if check and prev_v != self._icon_is_running:
            # update needed
            self._update_tray(update_icon=True)


if __name__ == '__main__':
    MainTray(timedelta(seconds=4)).run()
    # sg.preview_all_look_and_feel_themes()
