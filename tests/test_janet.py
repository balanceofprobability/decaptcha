import os
import time
from subprocess import Popen

import pyautogui
import pytest
from decaptcha.notarobot import NotARobot, OpenGround


class TestJanet:
    def test_browser_setup(self):
        Popen("chromium-browser https://www.google.com/recaptcha/api2/demo", shell=True)

    @pytest.fixture(scope="session")
    def janet(self):
        janet = NotARobot()
        janet.set_model("yolo.h5")
        return janet

    def test_janet(self, janet):
        janet.run()
        assert isinstance(janet.state.victory, bool)

    def test_janet_reset(self, janet):
        janet.reset()
        assert isinstance(janet.state, OpenGround)
