import logging
from datetime import timedelta, timedelta as delta
from typing import Dict, List, Optional, Tuple, Union

import PySimpleGUIQt as sg
from computerSitTimer.CountDowner import CountDowner
from PySimpleGUIQt import SystemTray

from computerSitTimer.media.MediaHelper import get_icon_path

logging.warning(sg.version)
logging.warning(sg.sys.version)

sg.theme('DarkTanBlue')  # Add a touch of color


class Const:
    """
    A namespace instead of a class to have all constants
    """
    timeout_popup = 333  # in milliseconds
    timeout_tray = 1000  # in milliseconds
    timeout_core = 1000  # in milliseconds


class PopUp:
    timer: CountDowner

    currentTimeKey = '_time_'
    msgKey = '_msg_'
    negativeFontColor = '#df0000'
    font = 'Helvetica'
    durationKey = "_duration_"
    durationFormat = "mm, mm:ss or hh:mm:ss"

    def __init__(self, core: CountDowner):
        self.core = core
        self.keepOnTop = True
        self.start_minimised = True

        layout = [[sg.Text('', key=self.msgKey, size=(20, 1), auto_size_text=True, font=(self.font, 20),
                           justification='center')],
                  [sg.Text('Current time: '), sg.Text('', key=self.currentTimeKey, size=(20, 1))],
                  [sg.Text('Full time: '), sg.Input(self.core.duration, key=self.durationKey,
                                                    tooltip=f"in the format {self.durationFormat}",
                                                    enable_events=True),
                   sg.Button('Set', button_color=('white', '#FF8800'), bind_return_key=True)],
                  [sg.Button('Start', button_color=('white', '#00FF00')),
                   sg.Button('Stop', button_color=('white', '#FF0000')),
                   sg.Button('Reset', button_color=('white', '#FF8800'))],
                  [sg.Quit()]]
        self.window = sg.Window(title='Simple Clock', layout=layout, keep_on_top=self.keepOnTop,
                                icon=get_icon_path(True))  # , icon=)
        self.normalFontColor = self.window[self.currentTimeKey].TextColor
        self.run_window_loop()

    def bringToFront(self) -> None:
        """ Because unsetting window.KeepOnTop does not work properly """
        # self.window.TKroot.wm_attributes("-topmost", 1)
        self.window.BringToFront()

    def bringToFrontReset(self) -> None:
        if not self.keepOnTop:
            self.window.KeepOnTop = False
            # self.window.TKroot.wm_attributes("-topmost", 0)

    def updateTime(self):
        to_notify, time_str, seconds_left = self.core.get_updated_state_and_time()
        logging.debug(f"-- UI update: {time_str}")
        self.window[self.currentTimeKey].Update(time_str, text_color=(self.normalFontColor if seconds_left >= 0 else
                                                                      self.negativeFontColor))
        if to_notify:
            self.bringToFront()
            self.core.done_and_turn_off_noti()
            # sg.popup_non_blocking(f"Time's up! {self.cd_obj.fmtDelta(self.cd_obj.duration)}")
        if seconds_left < 0 and len(self.window[self.msgKey].DisplayText) == 0:
            self.window[self.msgKey].Update("Time's up!")

    def run_window_loop(self) -> None:
        # Event loop
        while True:
            event, values = self.window.Read(timeout=Const.timeout_popup)

            # Exits program cleanly if user clicks "X" or "Quit" buttons
            if event in (sg.WIN_CLOSED, 'Quit'):
                seconds_left = self.core.get_updated_state_and_time()[2]
                if seconds_left < 0:
                    self.core.reset()
                self.window.close()
                break
            elif event in ["Start", "Stop", "Reset"]:
                self.core.call_event_by_str(event)
                if event == "Reset":
                    self.window[self.msgKey].Update('')
                    self.bringToFrontReset()
            elif event in ["Set"]:
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
                    sg.Popup(f"Invalid duration format! It must be in the form of {self.durationFormat}.",
                             keep_on_top=True)
                else:
                    self.core.set(timedelta(hours=duration[0], minutes=duration[1], seconds=duration[2]))

            elif event == "__TIMEOUT__":
                pass
            else:
                pass
            self.updateTime()


class MainTray:
    """
    The Main class, basically the tray object.
    So now tray will be the master, and when time is up, it will make a (blocking) call to show the UI.
    Tray will run at all time while Ui is not required.
    """
    timer: CountDowner
    tray: Optional[SystemTray]
    _state: Dict[str, bool]

    def __init__(self, timer: CountDowner):
        self.timer = timer
        self.tray: Optional[sg.SystemTray] = None
        self._state = self._getTrayState()

    def createMenuList(self) -> List[List[str]]:
        """ A specific function so that sound option can be set accordingly"""
        menu_def = ['UNUSED', ['Start', 'Stop', 'Reset', "---",
                               "Show UI", "---",
                               'Exit']]
        return menu_def

    def createTray(self):
        self.tray = sg.SystemTray(**self._getUpdateTrayKwargs(update_time=True, update_menu=True, update_icon=True))
        self._checkState(True)

    def showUi(self):
        """blocking call to show Ui"""
        # t = Thread(target=Ui, args=(self.core, ))
        # t.start()
        PopUp(self.timer)

    def run(self):
        self.createTray()
        """running the main loop"""
        while True:
            event = self.tray.Read(timeout=Const.timeout_tray)

            # Exits program cleanly if user clicks "X" or "Quit" buttons
            if event == 'Exit':
                self.tray.close()
                break
            elif event in ["Start", "Stop", "Reset"]:
                self.timer.call_event_by_str(event)
                self._updateTrayAll()
            elif event == sg.EVENT_TIMEOUT:
                pass
            elif event in ("Show UI", sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
                self.showUi()
            else:
                logging.debug(event.__repr__())
            self._checkState()
            if self._toNotify():
                logging.debug("tray calling UI as time's up")
                self.showUi()

    def _toNotify(self) -> bool:
        to_notify, time_str, seconds_left = self.timer.get_updated_state_and_time()
        self._updateTray(time_str)
        logging.debug(f"-- tray update: {time_str}")
        if to_notify:
            self.tray.ShowMessage("Time is up!", "Move your ass away from the chair please!")
        return to_notify

    def _updateTray(self, time_str: Optional[str] = None, update_time=False, update_icon=False,
                    update_menu=False) -> None:
        """Update menu, tray icon etc"""
        self.tray.update(
            **self._getUpdateTrayKwargs(time_str=time_str, update_time=update_time, update_icon=update_icon,
                                        update_menu=update_menu))

    def _updateTrayAll(self):
        self._updateTray(update_menu=True, update_icon=True, update_time=True)
        self._checkState(True)

    def _getUpdateTrayKwargs(self, time_str: Optional[str] = None, update_time: bool = False, update_icon: bool = False,
                             update_menu: bool = False):
        update_kwargs = {}
        if time_str is not None:
            update_kwargs.update(tooltip=time_str)
        elif update_time:
            update_kwargs.update(tooltip=self.timer.get_updated_state_and_time()[1])
        if update_icon:
            update_kwargs.update(filename=get_icon_path(self.timer.is_running()))
        if update_menu:
            update_kwargs.update(menu=self.createMenuList())
        return update_kwargs

    def _getTrayState(self):
        """ without time """
        return {"timer": self.timer.is_running()}

    def _checkState(self, override_only=False):
        """ When override_only, just update the state.
        Otherwise, if there are changes, update to the tray will be followed automatically
        """
        if override_only:
            self._state = self._getTrayState()
            return

        old_state = self._state
        self._state = self._getTrayState()
        update_kwargs = {}
        if old_state["timer"] != self._state["timer"]:
            update_kwargs.update(update_icon=True)
        if update_kwargs:
            self._updateTray(**update_kwargs)


class UiCoreInterface:
    """
    Simple center processor of user input.

    """
    ui_s: Dict[str, Union[MainTray, Optional[PopUp]]]
    timer: CountDowner

    def __init__(self, timer_time: timedelta):
        self.timer = CountDowner(duration=timer_time)
        self.ui_s = {"tray": MainTray(self.timer), "popup": None}

    def run(self):
        self.ui_s["tray"].run()


if __name__ == '__main__':
    if False:
        sg.preview_all_look_and_feel_themes()
