import pathlib
from pathlib import Path

_mediaDirPath: Path = pathlib.Path(__file__).parent.absolute()


def get_abs_path(filename: str) -> str:
    abs_path = _mediaDirPath / filename
    print(str(abs_path))
    print(pathlib.Path().absolute())
    assert(abs_path.exists()), f"Invalid file {filename}!"
    return str(abs_path)
