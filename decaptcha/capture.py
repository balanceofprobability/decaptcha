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
    from os import getcwd
    from pyautogui import center
    from pyautogui import locateOnScreen
    from time import sleep

    try:
        button = locateOnScreen(getcwd() + "/decaptcha/skip.png", confidence=0.7)
    except:
        button = locateOnScreen(getcwd() + "/decaptcha/verify.png", confidence=0.7)
    ctr = center(button)
    top = str(ctr.y - 550)
    left = str(ctr.x - 342)
    capture(top, left, 402, 530, "target.png")
