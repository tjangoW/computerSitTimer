import PySide2 as Ps
import sys

# somehow I managed to installed PySide2=5.11 in python=3.8 without pip complaining!
# This is not run during pip install by in __main__, for 1: simplicity, 2: not sure the sequence package is installed 
assert not (sys.version_info > (3, 8) and Ps.__version_info__ < (5, 14)), \
    f"PySide2=v{Ps.__version__} is less than 5.14 and does not support Python>=3.8"
