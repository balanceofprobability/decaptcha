from os import getcwd
from random import seed
from random import randint
from random import uniform
from pyautogui import center
from pyautogui import click
from pyautogui import moveTo
from pyautogui import easeOutQuad
from pyautogui import locateOnScreen
from time import sleep

seed()


def humanclick(imnotarobot: str) -> None:
    ctr = center(imnotarobot)
    loops = randint(1, 3)
    x_offset = uniform(-100, 100)
    y_offset = uniform(-100, 100)
    for _ in range(loops):
        moveTo(ctr.x - 124 + x_offset, ctr.y + y_offset, uniform(0.1, 0.3), easeOutQuad)
        x_offset = x_offset * uniform(0.5, 0.9)
        y_offset = y_offset * uniform(0.5, 0.9)
        # sleep(uniform(0, 1))
    moveTo(
        ctr.x - 124 + randint(-10, 10),
        ctr.y + randint(-10, 10),
        uniform(0.1, 0.5),
        easeOutQuad,
    )
    click()


if __name__ == "__main__":
    """from project directory"""
    imnotarobot = locateOnScreen(
        getcwd() + "/decaptcha/imnotarobot.png", confidence=0.7
    )
    humanclick(imnotarobot)
