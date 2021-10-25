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
    c2 = CountDowner(timedelta(seconds=ori_sec), direct_start=True)
    assert c2.is_running()

    c.stop()
    assert not c.is_running()
    assert not c._has_noti

    c.start()
    assert c.is_running()
    sleep(2)
    assert c.get_updated_state_and_time()[2] <= 2
    assert not c._time_is_up()
    assert not c._has_noti

    c.start()
    assert c.is_running()
    sleep(2)
    assert c.get_updated_state_and_time()[2] < 0
    assert c._time_is_up()
    assert c._has_noti

    c.stop()
    assert not c.is_running()
    assert c.get_updated_state_and_time()[2] < 0
    assert c._time_is_up()
    assert c._has_noti

    c.done_and_turn_off_noti()
    assert c._time_is_up()
    assert not c._has_noti

    v1 = c.get_updated_state_and_time()
    sleep(1)
    v2 = c.get_updated_state_and_time()
    assert v1[0] == v2[0]
    assert v1[1] == v2[1]
    assert v1[2] == v2[2]

    c.reset()
    assert c.get_updated_state_and_time()[2] == ori_sec

    c.set(timedelta(minutes=5))
    assert c.get_updated_state_and_time()[2] == 5*60


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
