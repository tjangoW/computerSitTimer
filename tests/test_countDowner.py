from time import sleep

from computerSitTimer.CountDowner import CountDowner
from datetime import timedelta


def test_formatting():
    assert CountDowner.fmtDelta(timedelta(seconds=12, hours=32)) == " 32:00:12"
    assert CountDowner.fmtDelta(timedelta(minutes=121, seconds=51)) == " 02:01:51"


def test_start_stop_set():
    ori_sec = 4
    c = CountDowner(timedelta(seconds=ori_sec))
    assert c.is_stopped()
    assert not c.is_running()

    c.stop()
    assert c.is_stopped()
    assert not c.is_running()

    c.start()
    assert not c.is_stopped()
    assert c.is_running()
    sleep(2)
    assert c.get_time()[1] <= 2

    c.start()
    assert not c.is_stopped()
    assert c.is_running()
    sleep(2)
    assert c.get_time()[1] < 0

    c.stop()
    assert c.is_stopped()
    assert not c.is_running()
    assert c.get_time()[1] < 0

    v1 = c.get_time()
    sleep(1)
    v2 = c.get_time()
    assert v1[0] == v2[0]
    print(v2)

    c.reset()
    assert c.get_time()[1] == ori_sec

    c.set(timedelta(minutes=5))
    assert c.get_time()[1] == 5*60


def test_create_from_settings():
    c = CountDowner(timedelta(seconds=2))
    c.start()
    sleep(3)
    c.stop()
    settings = c.get_setting()

    c2 = CountDowner(**settings)
    assert c.duration == c2.duration
    assert c.remaining_time == c2.remaining_time
    assert c.is_running() == c2.is_running()

    print(c2)
