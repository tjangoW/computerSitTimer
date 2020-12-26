import logging as log
from datetime import timedelta

from computerSitTimer.Ui import MainTray

if __name__ == "__main__":
    log.basicConfig(format='%(levelname)s:%(message)s', level=log.INFO)
    m = MainTray(timedelta(hours=1))

    m.run()
