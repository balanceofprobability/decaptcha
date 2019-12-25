import os
import time

import pyautogui
import pytest
import Xlib.display
from selenium import webdriver

from decaptcha.notarobot import NotARobot, OpenGround


@pytest.fixture(scope="session")
def browser():
    return webdriver.Firefox()


def test_browser_setup(browser):
    browser.maximize_window()
    browser.get("https://www.google.com/recaptcha/api2/demo")


def test_title(browser):
    assert "ReCAPTCHA demo" in browser.title


def test_x11_display():
    pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ["DISPLAY"])


@pytest.fixture(scope="session")
def bot():
    bot = NotARobot()
    bot.set_model("yolo.h5")
    return bot


def test_bot(bot):
    bot.run()
    assert bot.state.victory == True or bot.state.killswitch == True


def test_reset(bot):
    bot.reset()
    assert isinstance(bot.state, OpenGround)


def test_teardown(browser):
    browser.close()
    browser.quit()
