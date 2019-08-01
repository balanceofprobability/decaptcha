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
    greyinvert: bool = True,
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

        if greyinvert == True:
            inverted_image = PIL.ImageOps.invert(image).convert("LA")
            inverted_image.save("greyinvert_" + filename)


if __name__ == "__main__":
    from os import getcwd
    from pyautogui import center
    from pyautogui import locateOnScreen
    import time

    # Attempt to locate recaptcha test on screen
    starttimer = time.time()
    while time.time() - starttimer < 30:
        try:
            button = locateOnScreen(getcwd() + "/decaptcha/skip.png", confidence=0.7)
            print("skip")
            break
        except Exception as e:
            button = locateOnScreen(getcwd() + "/decaptcha/verify.png", confidence=0.7)
            print("verify")
            break
        else:
            print(e)

    top = int(button.top) - 550 + 29
    left = int(button.left) - 342 + 58
    capture(top, left, 402, 530, "puzzle.png")
