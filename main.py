# This is a sample Python script.

# Press Ctrl+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from enum import Enum
from typing import Optional, Union

import PySimpleGUI as sg
import datetime
from datetime import datetime as dt
from datetime import timedelta as delta

void = None

sg.theme('DarkTanBlue')  # Add a touch of color

# All the stuff inside your window.
# layout = [[sg.Text('Your typed chars appear here:'), sg.Text(size=(15, 1), key='-OUTPUT-')],
#           [sg.Input(key='-IN-')],
#           [sg.Button('Show'), sg.Button('Exit')],
#           [sg.Button("Choose Color", button_type=sg.BUTTON_TYPE_COLOR_CHOOSER)]]


class CountDowner:
    class Status(Enum):
        STARTED = 1
        STOPPED = 0

    def __init__(self, duration: delta = delta(hours=1)):
        self.duration = duration
        self.remaining_time = duration
        self.status = self.Status.STOPPED
        self._previous_update_time: Optional[dt] = None  # helper variable to update the counter

    def start(self) -> void:
        if self.status == self.Status.STARTED:
            return
        self.status = self.Status.STARTED
        self._previous_update_time = dt.now()

    def _update_time(self) -> void:
        if self.status == self.Status.STOPPED:
            return
        time_passed = dt.now() - self._previous_update_time
        self.remaining_time -= time_passed
        self._previous_update_time += time_passed

    def stop(self) -> void:
        if self.status == self.Status.STOPPED:
            return
        self._update_time()
        self.status = self.Status.STOPPED
        self._previous_update_time = None

    def set(self, duration: delta) -> void:
        self.stop()
        self.duration = duration
        self.remaining_time = duration

    def reset(self) -> void:
        self.stop()
        self.remaining_time = self.duration

    @classmethod
    def fmtDelta(cls, t: delta) -> str:
        ts = t.total_seconds()
        tm, ss = divmod(abs(ts), 60)
        hh, mm = divmod(tm, 60)
        return f"{'-' if ts<0 else ' '}{hh:02.0f}:{mm:02.0f}:{ss:02.0f}"

    def get_time(self) -> str:
        self._update_time()
        return self.fmtDelta(self.remaining_time)

    def __repr__(self) -> str:
        self._update_time()
        return f"{self.__class__.__name__} ({self.status}), Duration={self.fmtDelta(self.duration)}, " \
               f"left={self.fmtDelta(self.remaining_time)}"


if __name__ == '__main__':
    c = CountDowner()
    c.start()
    c.get_time()
    # KEY DEFINITIONS
    # _time_ = text field that displays time

    # Create the layout

    timeKey = '_time_'

    # show window
    def showWindow(cd_instance: CountDowner, timeout=100) -> void:
        layout = [[sg.Text('Time: '), sg.Text('', key=timeKey, size=(20, 1))],
                  [sg.Button('Start'), sg.Button('Stop'), sg.Button('Reset')],
                  [sg.Quit()]]
        window = sg.Window(title='Simple Clock', layout=layout)

        timeNormalColor = window[timeKey].TextColor
        timeNegativeColor = '#df0000'

        def updateTimeDisplay(timeDisplay_obj: sg.Text = window[timeKey]):
            s = cd_instance.remaining_time.total_seconds()
            timeDisplay_obj.Update(cd_instance.get_time(), text_color=(timeNegativeColor if s < 0 else timeNormalColor))

        # Event loop
        while True:
            event, values = window.Read(timeout=timeout)

            # Exits program cleanly if user clicks "X" or "Quit" buttons
            if event in (sg.WIN_CLOSED, 'Quit'):
                window.close()
                break
            elif event == 'Start':
                cd_instance.start()
            elif event == 'Stop':
                cd_instance.stop()
            elif event == 'Reset':
                cd_instance.reset()
            updateTimeDisplay()


    cd1 = CountDowner(delta(seconds=5))
    showWindow(cd1)

