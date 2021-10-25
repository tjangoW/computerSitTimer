from time import sleep

from computerSitTimer.CountDowner import CountDowner
from datetime import timedelta


def test_formatting():
    assert CountDowner.fmtDelta(timedelta(seconds=12, hours=32)) == " 32:00:12"
    assert CountDowner.fmtDelta(timedelta(minutes=121, seconds=51)) == " 02:01:51"


def test_start_stop_set():
    ori_sec = 4
    c = CountDowner(timedelta(seconds=ori_sec), direct_start=False)
    assert not c.is_running()
    assert not c._has_noti

    c.stop()
    assert not c.is_running()
    assert not c._has_noti

    c.start()
    assert c.is_running()
    sleep(2)
    assert c.get_updates()[2] <= 2
    assert not c._time_is_up()
    assert not c._has_noti

    c.start()
    assert c.is_running()
    sleep(2)
    assert c.get_updates()[2] < 0
    assert c._time_is_up()
    assert c._has_noti

    c.stop()
    assert not c.is_running()
    assert c.get_updates()[2] < 0
    assert c._time_is_up()
    assert c._has_noti

    c.done_and_turn_off_noti()
    assert c._time_is_up()
    assert not c._has_noti

    v1 = c.get_updates()
    sleep(1)
    v2 = c.get_updates()
    assert v1[0] == v2[0]
    assert v1[1] == v2[1]
    assert v1[2] == v2[2]

    c.reset()
    assert c.get_updates()[2] == ori_sec

    c.set(timedelta(minutes=5))
    assert c.get_updates()[2] == 5 * 60


def test_direct_start():
    c2 = CountDowner(timedelta(seconds=5), direct_start=True)
    assert c2.is_running()

    c2.stop()
    assert not c2.is_running()

    c2.reset()
    assert c2.is_running()
