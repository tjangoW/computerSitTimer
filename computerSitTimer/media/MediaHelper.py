from pathlib import Path

_mediaDirPath: Path = Path(__file__).parent.absolute()


def get_abs_path(filename: str) -> str:
    abs_path = _mediaDirPath / filename
    assert(abs_path.exists()), f"Invalid file {filename}!"
    return str(abs_path)


def get_icon_path(is_play: bool) -> str:
    filename = f"icon-{'play' if is_play else 'stop'}.png"
    return get_abs_path(filename)
