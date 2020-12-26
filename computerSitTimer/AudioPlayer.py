import logging as log
from typing import Optional, Any, Union, Dict
import simpleaudio as sa
from simpleaudio import PlayObject


def _has(obj: Optional[Any]):
    return obj is not None


class AudioPlayer:
    """
    Yet another wrapper to the simpleaudio.
    Try not to load a audio that is too large at it will be loaded into memory during __init__.
    """
    wav_filename: Optional[str]
    is_sound_on: bool
    _play_obj: Optional[PlayObject]
    _wav_obj: Optional[sa.WaveObject]

    def __init__(self, wav_filename: Optional[str], is_sound_on: bool = True):
        self.is_sound_on = is_sound_on
        self.wav_filename = wav_filename
        self._wav_obj = sa.WaveObject.from_wave_file(wav_filename) if _has(wav_filename) else None
        self._play_obj = None

    def getSetting(self) -> Dict[str, Union[Optional[str], bool]]:
        return {
            "wav_filename": self.wav_filename,
            "is_sound_on": self.is_sound_on,
        }

    def play(self):
        if not self.is_sound_on:
            return
        if not _has(self._wav_obj):
            log.warning("Playing empty audio")
            return
        if _has(self._play_obj) and self._play_obj.is_playing():
            # If it is already playing, nothing will be done
            return
        self._play_obj = self._wav_obj.play()

    def stop(self):
        if _has(self._play_obj):
            self._play_obj.stop()

    def on(self):
        self.is_sound_on = True

    def off(self):
        self.is_sound_on = False

    def toggle_sound(self):
        self.is_sound_on = not self.is_sound_on
        # could be fancier with ^=1 but maybe not

    def __del__(self):
        self.stop()


if __name__ == '__main__':
    p = AudioPlayer("media/River_birds-1m.mp3.wav")
    from time import sleep

    p.play()

    sleep(2)
    p.stop()
    sleep(1)
    p.play()
    sleep(1)

    p = AudioPlayer("media/River_birds-1m.mp3.wav")
