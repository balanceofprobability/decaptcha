from random import seed
from random import randint
from random import uniform
from pyautogui import click
from pyautogui import moveTo
from pyautogui import easeOutQuad
from time import sleep
from typing import Tuple

seed()


def human_click(left: int, top: int, right: int, bottom: int) -> Tuple[int, int]:
    """Click within a specified region, like a human"""
    loops = randint(0, 2)
    target_x = randint(left, right)
    target_y = randint(top, bottom)
    x_offset = uniform(-100, 100)
    y_offset = uniform(-100, 100)
    for _ in range(loops):
        moveTo(target_x + x_offset, target_y + y_offset, uniform(0.1, 0.3), easeOutQuad)
        x_offset = x_offset * uniform(0.5, 0.9)
        y_offset = y_offset * uniform(0.5, 0.9)
        # sleep(uniform(0, 1))
    moveTo(target_x, target_y, uniform(0.1, 0.5), easeOutQuad)
    click(target_x, target_y)
    return target_x, target_y


if __name__ == "__main__":
    """from project directory"""
    from os import getcwd
    from pyautogui import locateCenterOnScreen

    imnotarobot = locateCenterOnScreen(
        getcwd() + "/decaptcha/imnotarobot.png", confidence=0.7
    )
    # Click "I'm not a robot" button like a human
    left = imnotarobot.x - 124 - 10
    top = imnotarobot.y - 10
    right = left + 20
    bottom = top + 20
    human_click(left, top, right, bottom)
