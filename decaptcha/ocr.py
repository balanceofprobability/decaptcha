try:
    from PIL import Image
except ImportError:
    import Image
import re
from typing import Optional

from tesserocr import image_to_text


def ocr(
    img: "Image",
    left: Optional[int] = 0,
    upper: Optional[int] = 0,
    right: Optional[int] = None,
    lower: Optional[int] = None,
) -> Optional[str]:
    """Takes an image object and returns a string dump of specified region, using optical character recognition."""
    try:
        selection = img.crop((left, upper, right, lower))
    except:
        selection = img
    stringdump = image_to_text(selection)
    try:
        return re.sub("[^A-Za-z ]+", "", stringdump)
    except:
        return stringdump


if __name__ == "__main__":
    """
    cmd usage:
    $ python ocr.py 0 0 50 50
    """
    from sys import argv
    import pyscreenshot as ImageGrab

    img = ImageGrab.grab()

    try:
        print(ocr(img, int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4])))
    except:
        print(ocr(img))
