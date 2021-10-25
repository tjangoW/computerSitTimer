import logging as log
import sys
from datetime import timedelta

from computerSitTimer.GraphicalUI import MainTray


def main(args=None):
    # from https://chriswarrick.com/blog/2014/09/15/python-apps-the-right-way-entry_points-and-scripts/
    if args is None:
        args = sys.argv[1:]

    m = MainTray(timedelta(hours=1))
    # m = MainTray(timedelta(seconds=4))
    m.run()


if __name__ == "__main__":
    log.basicConfig(format='%(levelname)s:%(message)s', level=log.INFO)
    sys.exit(main())
