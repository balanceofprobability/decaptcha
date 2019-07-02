import mss
from typing import Union
from PIL import Image
import PIL.ImageOps


def capture(
    top: Union[int, str],
    left: Union[int, str],
    width: Union[int, str],
    height: Union[int, str],
    filename: str,
):
    with mss.mss() as sct:
        # The screen part to capture
        region = {
            "top": int(top),
            "left": int(left),
            "width": int(width),
            "height": int(height),
        }

        # Grab the data
        img = sct.grab(region)

        # Save to the picture file
        mss.tools.to_png(img.rgb, img.size, output=filename)

        image = Image.open(filename)
        inverted_image = PIL.ImageOps.invert(image).convert("LA")
        inverted_image.save("greyinvert_" + filename)


if __name__ == "__main__":
    """
    cmd usage:
    $ python capture.py 50 50 100 100 test.png
    """
    from sys import argv

    top = argv[1]
    left = argv[2]
    width = argv[3]
    height = argv[4]
    print(capture(top, left, width, height, argv[5]))
