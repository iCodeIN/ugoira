import pathlib
import zipfile

from pytest import fixture

from wand.color import Color
from wand.image import Image


@fixture
def fx_tmpdir(tmpdir):
    """Make :class:`pathlib.Path` instance of ```tmpdir```."""

    return pathlib.Path(str(tmpdir))


@fixture
def fx_ugoira_body():
    """Ugoira page data."""

    with open('./tests/mock/ugoira.json') as f:
        return f.read().encode('u8')


@fixture
def fx_non_ugoira_body():
    """Non ugoira page data."""

    with open('./tests/mock/non_ugoira.json') as f:
        return f.read().encode('u8')


@fixture
def fx_ugoira_zip(fx_tmpdir):
    """
    Generates a zip file used in testing
    instead of downloading an actual ugoira.
    """

    file = fx_tmpdir / '00000000_ugoira600x600.zip'
    imgs = [
        fx_tmpdir / '000000.jpg',
        fx_tmpdir / '000001.jpg',
        fx_tmpdir / '000002.jpg',
    ]
    colors = [
        Color('red'),
        Color('blue'),
        Color('green'),
    ]
    for path, color in zip(imgs, colors):
        with Image(width=100, height=100, background=color) as img:
            img.save(filename=str(path))

    with zipfile.ZipFile(str(file), 'w') as f:
        for img in imgs:
            f.write(str(img), img.name)

    with file.open('rb') as f:
        return f.read()


@fixture
def fx_ugoira_frames():
    """frames data."""

    return {
        '000000.jpg': 1000,
        '000001.jpg': 2000,
        '000002.jpg': 3000,
    }
