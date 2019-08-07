try:
    from PIL import Image
except ImportError:
    import Image
from pytesseract import image_to_string
from typing import Optional
import re


def ocr(
    filename: str,
    left: Optional[int] = 0,
    upper: Optional[int] = 0,
    right: Optional[int] = None,
    lower: Optional[int] = None,
) -> Optional[str]:
    """Simple image to string"""
    img = Image.open(filename)
    try:
        selection = img.crop((left, upper, right, lower))
    except:
        right = img.width
        lower = img.height
        selection = img.crop((left, upper, right, lower))
    stringdump = image_to_string(selection)
    try:
        return re.sub("[^A-Za-z ]+", "", stringdump)
    except:
        return stringdump


if __name__ == "__main__":
    """
    cmd usage:
    $ python ocr filename.png 0 0 50 50
    """
    from sys import argv

    try:
        print(ocr(argv[1], int(argv[2]), int(argv[3]), int(argv[4]), int(argv[5])))
    except:
        print(ocr(argv[1]))
