import logging as log
# from threading import Thread
# noinspection PyPep8Naming
import PySimpleGUIQt as sg
from typing import Optional, List, Dict, Union

from PySimpleGUIQt import SystemTray
from datetime import timedelta as delta, timedelta

from computerSitTimer.CoreWithoutUi import CoreBI
from computerSitTimer.media.MediaHelper import get_abs_path

log.warning(sg.version)
log.warning(sg.sys.version)

sg.theme('DarkTanBlue')  # Add a touch of color


class Const:
    """
    A namespace instead of a class to have all constants
    """
    timeout_ui = 333  # in milliseconds
    timeout_bg = 1000  # in milliseconds


class Ui:
    core: CoreBI

    currentTimeKey = '_time_'
    msgKey = '_msg_'
    negativeFontColor = '#df0000'
    font = 'Helvetica'
    durationKey = "_duration_"
    durationFormat = "mm, mm:ss or hh:mm:ss"

    def __init__(self, core: CoreBI):
        self.core = core

        layout = [[sg.Text('', key=self.msgKey, size=(20, 1), auto_size_text=True, font=(self.font, 20),
                           justification='center')],
                  [sg.Text('Current time: '), sg.Text('', key=self.currentTimeKey, size=(20, 1))],
                  [sg.Text('Full time: '), sg.Input(self.core.getSetting("timer_time"), key=self.durationKey,
                                                    tooltip=f"in the format {self.durationFormat}",
                                                    enable_events=True),
                   sg.Button('Set', button_color=('white', '#FF8800'), bind_return_key=True)],
                  [sg.Button('Start', button_color=('white', '#00FF00')),
                   sg.Button('Stop', button_color=('white', '#FF0000')),
                   sg.Button('Reset', button_color=('white', '#FF8800'))],
                  [sg.Quit()]]
        self.window = sg.Window(title='Simple Clock', layout=layout, keep_on_top=self.core.keepOnTop,
                                icon=get_abs_path("icon-play.png"))  # , icon=)
        self.normalFontColor = self.window[self.currentTimeKey].TextColor
        self.run_window_loop()

    def bringToFront(self) -> None:
        """ Because unsetting window.KeepOnTop does not work properly """
        # self.window.TKroot.wm_attributes("-topmost", 1)
        self.window.BringToFront()

    def bringToFrontReset(self) -> None:
        if not self.core.keepOnTop:
            self.window.KeepOnTop = False
            # self.window.TKroot.wm_attributes("-topmost", 0)

    def updateTime(self):
        to_notify, time_str, seconds_left = self.core.updateTime()
        log.debug(f"-- UI update: {time_str}")
        self.window[self.currentTimeKey].Update(time_str, text_color=(self.normalFontColor if seconds_left >= 0 else
                                                                      self.negativeFontColor))
        if to_notify:
            self.bringToFront()
            self.core.offToNotifyState()
            # sg.popup_non_blocking(f"Time's up! {self.cd_obj.fmtDelta(self.cd_obj.duration)}")
        if seconds_left < 0 and len(self.window[self.msgKey].DisplayText) == 0:
            self.window[self.msgKey].Update("Time's up!")

    def run_window_loop(self) -> None:
        # Event loop
        while True:
            event, values = self.window.Read(timeout=Const.timeout_ui)

            # Exits program cleanly if user clicks "X" or "Quit" buttons
            if event in (sg.WIN_CLOSED, 'Quit'):
                seconds_left = self.core.updateTime()[2]
                if seconds_left < 0:
                    self.core.reset()
                self.window.close()
                break
            elif event in ["Start", "Stop", "Reset"]:
                self.core.changeEvents(event)
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
    core: CoreBI
    tray: Optional[SystemTray]
    _state: Dict[str, bool]

    def __init__(self, timer_time: timedelta, sound_on: bool = False, sound_file: Optional[str] = None):
        self.core = CoreBI(timer_time=timer_time, sound_on=sound_on, sound_file=sound_file)
        self.tray: Optional[sg.SystemTray] = None
        self._state = self._getTrayState()

    def createMenuList(self) -> List[List[str]]:
        """ A specific function so that sound option can be set accordingly"""
        menu_def = ['UNUSED', ['Start', 'Stop', 'Reset', "---",
                               f"Sound: {'ON' if self.core.noti_player.is_sound_on else 'OFF'}", "---",
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
        Ui(self.core)

    def run(self):
        self.createTray()
        """running the main loop"""
        while True:
            event = self.tray.Read(timeout=Const.timeout_bg)

            # Exits program cleanly if user clicks "X" or "Quit" buttons
            if event == 'Exit':
                self.tray.close()
                break
            elif event in ["Start", "Stop", "Reset"]:
                self.core.changeEvents(event)
                self._updateTrayAll()
            elif event == sg.EVENT_TIMEOUT:
                pass
            elif event.startswith("Sound: "):
                self.core.noti_player.toggle_sound()
                self._checkState()
            elif event in ("Show UI", sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
                self.showUi()
            else:
                log.debug(event.__repr__())
            self._checkState()
            if self._toNotify():
                log.debug("tray calling UI as time's up")
                self.showUi()

    def _toNotify(self) -> bool:
        to_notify, time_str, seconds_left = self.core.updateTime()
        self._updateTray(time_str)
        log.debug(f"-- tray update: {time_str}")
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
            update_kwargs.update(tooltip=self.core.updateTime()[1])
        if update_icon:
            update_kwargs.update(filename=get_abs_path(f"icon-{'play' if self.core.is_running() else 'stop'}.png"))
        if update_menu:
            update_kwargs.update(menu=self.createMenuList())
        return update_kwargs

    def _getTrayState(self):
        """ without time """
        return {"timer": self.core.is_running(), "sound": self.core.noti_player.is_sound_on}

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
        if old_state["sound"] != self._state["sound"]:
            update_kwargs.update(update_menu=True)
        if update_kwargs:
            self._updateTray(**update_kwargs)


if __name__ == '__main__':
    # well, I run this for debug, so 5 seconds
    # actual use is through __main__.py
    log.basicConfig(format='%(levelname)s:%(message)s', level=log.DEBUG)
    m = MainTray(delta(seconds=5))

    # c = m.core
    # t = Thread(target=Ui, args=(m.core,))
    # t.start()
    m.run()

if False:
    sg.preview_all_look_and_feel_themes()

    import queue

    queue_gui = queue.Queue()
    queue_gui.get_nowait()
