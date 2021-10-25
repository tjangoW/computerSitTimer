import logging
from datetime import timedelta
from typing import List, Optional, Union

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
    timeout_popup = 333  # in milliseconds
    timeout_tray = 1000  # in milliseconds


class PopUp:
    window: Optional[Window]
    normalFontColor: str
    timer: CountDowner

    currentTimeKey = '_time_'
    msgKey = '_msg_'
    negativeFontColor = '#df0000'
    font = 'Helvetica'
    durationKey = "_duration_"
    durationFormat = "mm, mm:ss or hh:mm:ss"

    def __init__(self, timer: CountDowner):
        self.timer = timer
        self.keepOnTop = True
        self.start_minimised = True
        self.window = None

    def create_window(self):
        layout = [[sg.Text('', key=self.msgKey, size=(20, 1),
                           auto_size_text=True, font=(self.font, 20),
                           justification='center')],
                  [sg.Text('Current time: '),
                   sg.Text('', key=self.currentTimeKey, size=(20, 1))],
                  [sg.Text('Full time: '),
                   sg.Input(self.timer.duration, key=self.durationKey,
                            tooltip=f"in the format {self.durationFormat}",
                            enable_events=True),
                   sg.Button(Event.SET, button_color=('white', '#FF8800'),
                             bind_return_key=True)],
                  [sg.Button(Event.START, button_color=('white', '#00FF00')),
                   sg.Button(Event.STOP, button_color=('white', '#FF0000')),
                   sg.Button(Event.RESET, button_color=('white', '#FF8800'))],
                  [sg.Quit(Event.CLOSE_POPUP)]]

        self.window = Window(title='Simple Clock', layout=layout,
                             keep_on_top=self.keepOnTop,
                             icon=get_icon_path(True))
        self.normalFontColor = self.window[self.currentTimeKey].TextColor

    def _update_time(self):
        to_notify, time_str, seconds_left = self.timer.get_updated_state_and_time()
        logging.debug(f"-- UI update: {time_str}")
        self.window[self.currentTimeKey].Update(time_str, text_color=(
            self.normalFontColor if seconds_left >= 0 else
            self.negativeFontColor))
        if to_notify:
            self.timer.done_and_turn_off_noti()
            # sg.popup_non_blocking(f"Time's up! {self.cd_obj.fmtDelta(self.cd_obj.duration)}")
        if seconds_left < 0 and len(self.window[self.msgKey].DisplayText) == 0:
            self.window[self.msgKey].Update("Time's up!")

    def run(self) -> None:
        self.create_window()
        # Event loop
        while True:
            event, values = self.window.Read(timeout=Const.timeout_popup)

            # Exits program cleanly if user clicks "X" or Event.ClosePopup buttons
            if event in (sg.WIN_CLOSED, Event.CLOSE_POPUP):
                seconds_left = self.timer.get_updated_state_and_time()[2]
                if seconds_left < 0:
                    self.timer.reset()
                self.window.close()
                break
            elif event in [Event.START, Event.STOP, Event.RESET]:
                self.timer.call_event_by_str(event)
                if event == Event.RESET:
                    self.window[self.msgKey].Update('')
            elif event in [Event.SET]:
                edit = self.window[self.durationKey]
                duration: List[Union[str, int]] = edit.Get().split(":")

                hasError: bool = False
                for _i in range(1):  # a fake loop to have breaking mechanism
                    if len(duration) not in [1, 2, 3]:
                        hasError = True
                        break
                    if len(duration) == 2:
                        duration.insert(0, "0")
                    elif len(duration) == 1:
                        duration = ["0", duration[0], "0"]
                    try:
                        duration = [int(i) for i in duration]
                    except ValueError:
                        hasError = True
                        break

                if hasError:
                    sg.Popup(
                        f"Invalid duration format! It must be in the form of {self.durationFormat}.",
                        keep_on_top=True)
                else:
                    self.timer.set(
                        timedelta(hours=duration[0], minutes=duration[1],
                                  seconds=duration[2]))

            elif event in (sg.EVENT_TIMEOUT, ):
                pass
            else:
                pass
            self._update_time()


class MainTray:
    """
    The Main class, basically the tray object.
    So now tray will be the master, and when time is up, it will make a
    (blocking) call to show the UI.
    Tray will run at all time while Ui is not required.
    """
    timer: CountDowner
    tray: Optional[SystemTray]
    icon_is_running: bool

    def __init__(self, delta: timedelta):
        self.timer = CountDowner(delta)
        self.tray = None  # none as multiprocessing cannot pickle QT object
        self.icon_is_running = self.timer.is_running()

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

    def _create_tray(self):
        self.tray = SystemTray()
        self._update_tray_all()

    def _show_popup(self):
        PopUp(self.timer).run()

    def run(self):
        self._create_tray()
        prev_is_running = self.timer.is_running()
        curr_is_running = prev_is_running
        """running the main loop"""
        while True:
            event = self.tray.Read(timeout=Const.timeout_tray)

            # Exits program cleanly if user clicks "X" or "Quit" buttons
            if event == Event.EXIT:
                self.tray.close()
                break
            elif event in [Event.START, Event.STOP, Event.RESET]:
                self.timer.call_event_by_str(event)
                self._update_tray_all()
                continue
            elif event in (
                    sg.EVENT_TIMEOUT, sg.EVENT_SYSTEM_TRAY_ICON_ACTIVATED):
                pass
            elif event in (
                    "Show UI", sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
                self._show_popup()
            else:
                logging.debug(event.__repr__())
                raise RuntimeError(f"Unhandled event: {event!r}")

            self._normal_time_update()

    def _normal_time_update(self):
        self._additional_icon_check_and_update()
        has_noti, time_str, _ = self.timer.get_updated_state_and_time()
        self._update_tray(time_str)
        if has_noti:
            logging.debug(f"-- tray update: {time_str}")
            self.tray.ShowMessage("Time is up!",
                                  "Move your ass away from the chair please!")
            logging.debug("tray calling UI as time's up")
            self.timer.done_and_turn_off_noti()
            self._show_popup()

    def _update_tray(self, time_str: Optional[str] = None, update_time=False,
                     update_icon=False, update_menu=False) -> None:
        """Update menu, tray icon etc"""

        update_kwargs = {}
        if time_str is not None:
            update_kwargs.update(tooltip=time_str)
        elif update_time:
            update_kwargs.update(
                tooltip=self.timer.get_updated_state_and_time()[1])
        if update_icon:
            update_kwargs.update(
                filename=get_icon_path(self.timer.is_running()))
            self._additional_icon_check_and_update(False)
        if update_menu:
            update_kwargs.update(menu=self._create_menu_list())
        self.tray.update(**update_kwargs)

    def _update_tray_all(self):
        self._update_tray(update_menu=True, update_icon=True, update_time=True)

    def _additional_icon_check_and_update(self, check=True):
        """check if the current timer icon fits with the timer state"""
        prev_v = self.icon_is_running
        self.icon_is_running = self.timer.is_running()

        if check and prev_v != self.icon_is_running:
            # update needed
            self._update_tray(update_icon=True)


if __name__ == '__main__':
    MainTray(timedelta(seconds=4)).run()
# sg.preview_all_look_and_feel_themes()
