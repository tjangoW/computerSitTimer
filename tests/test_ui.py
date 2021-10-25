import logging
from datetime import timedelta

from computerSitTimer.GraphicalUI import MainTray
from tests.TestHelper import run_ability_check_of_not_ending_function


def test_tray_run():
    """just to make sure it can run """
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    m = MainTray(timedelta(seconds=2))
    run_ability_check_of_not_ending_function(target=m.run, args=(), timeout=5)
    pass
