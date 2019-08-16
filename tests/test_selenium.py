from decaptcha import *
import pytest
import pyautogui
from pyvirtualdisplay import Display
from selenium import webdriver
import time
import os
import Xlib.display


@pytest.fixture(scope="session")
def vdisplay():
    return Display(visible=0, size=(1280, 768))


def test_vdisplay_setup(vdisplay):
    vdisplay.start()


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


@pytest.fixture
def bot():
    return NotARobot()


def test_bot(bot):
    bot.run()
    assert bot.state.victory == True or bot.state.killswitch == True


def test_teardown(browser):
    browser.close()
    browser.quit()


def test_xvfb_teardown(vdisplay):
    vdisplay.stop()
