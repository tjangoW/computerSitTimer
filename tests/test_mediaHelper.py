from pathlib import Path

from computerSitTimer.media.MediaHelper import get_icon_path


def test_function():
    p = Path(get_icon_path(True))
    assert p.exists()
    assert p.name == "icon-play.png"
    p2 = Path(get_icon_path(False))
    assert p2.exists()
    assert p2.name == "icon-stop.png"
