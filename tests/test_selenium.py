from decaptcha import *
import pytest
import pyautogui
from selenium import webdriver
import time
import os
import Xlib.display


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


def test_teardown(browser):
    browser.close()
    browser.quit()
