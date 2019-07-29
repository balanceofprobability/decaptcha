from decaptcha.base import GroundState
from decaptcha.fsm import StateMachine
from decaptcha.capture import capture
from decaptcha.humanclick import humanclick
from decaptcha.ocr import ocr
from decaptcha.objectdetection import *
from os import getcwd
from pyautogui import locateOnScreen
from pyscreeze import Box
import random
import time
from typing import Dict, Optional, Set, Tuple, Union


class OpenGround(GroundState):
    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        print("Look for robot nazi...")
        starttime = time.time()
        while time.time() - starttime < 30:
            try:
                clicked = self.imnotarobot()
                print(clicked, time.time())
                break
            except:
                pass

    def next(self) -> GroundState:
        print("Transitioning states...")

        print("Look for button...")
        starttime = time.time()
        while time.time() - starttime < 30:
            try:
                button = self.findbutton()
                print("Button found!")
                time.sleep(random.uniform(4.5, 6.5))
                return FacileGround(button)
            except:
                pass
        print("No button found.")
        return Terminate()


class FacileGround(GroundState):
    def __init__(self, button: "Box", cached_puzzle: str = "gorn.png") -> None:
        self.button = button
        self.cached_puzzle = cached_puzzle

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

    def next(self) -> GroundState:
        print("Transitioning states...")
        try:
            cached_puzzle_loc = locateOnScreen(self.cached_puzzle, confidence=0.7)
            assert hasattr(cached_puzzle_loc, "left")
            return DifficultGround(self.button)
        except:
            return ContentiousGround(self.button)


class ContentiousGround(GroundState):
    def __init__(self, button: "Box") -> None:
        self.button = button

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        print("Look for puzzle...")
        starttime = time.time()
        while time.time() - starttime < 30:
            try:
                self.savepuzzle(self.button)
                print("Puzzle saved!")
                break
            except:
                pass

        print("Look for word of the day...")
        starttime = time.time()
        while time.time() - starttime < 10:
            try:
                self.word = self.extractword()
                print("Word of the day:", self.word)
            except:
                pass
            else:
                if "vehicles" in self.word:
                    self.word = "carsbusmotorcycles"
                break

    def next(self) -> GroundState:
        print("Transitioning states...")
        try:
            assert self.isclassifiable(self.word)
            return SeriousGround(self.button, self.word, time.time())
        except:
            pass
        return DesperateGround(self.button)


class DifficultGround(GroundState):
    def __init__(self, button: "Box") -> None:
        self.button = button

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        print("Refresh puzzle...")
        try:
            clicked = self.refreshpuzzle(self.button)
            print(clicked, time.time())
            time.sleep(random.uniform(0, 0.5))
        except Exception as e:
            print(e)
            pass

    def next(self) -> GroundState:
        print("Transitioning states...")
        starttime = time.time()
        while time.time() - starttime < 30:
            try:
                print("Look for whether button moved or disappeared...")
                button = self.findbutton()
                return FacileGround(button)
            except:
                pass
        print("No button found.")
        return Terminate()


class SeriousGround(GroundState):
    def __init__(
        self,
        button: "Box",
        word: str,
        timer: float,
        cached_artifacts: Dict[str, Tuple[int, int, int, int]] = dict(),
    ):
        self.button = button
        self.word = word
        self.timer = timer
        self.cached_artifacts = cached_artifacts
        self.clickcounter = 0

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        artifacts = dict()  # type: dict
        try:
            print("Locate blacklisted artifacts...")
            blacklist = self.locateblacklist(self.cached_artifacts)
            assert len(blacklist) > 0
        except:
            print("Find all artifacts matching word...")
            artifacts = self.extractartifacts(self.word)

            print("Select what looks new...")
            self.selectartifacts(self.button, artifacts)

            self.clickcounter = len(artifacts)
            print("Counter:", self.clickcounter)

            if self.clickcounter > 0:
                print("Await possible regenerated artifacts...")
                time.sleep(random.uniform(4.5, 5.5))

            print("Save puzzle...")
            self.savepuzzle(self.button)
        else:
            print("No blacklisted artifacts.")
            selected = artifacts

        print("Cache artifacts...")
        self.cached_artifacts = artifacts

    def next(self) -> GroundState:
        print("Transitioning states...")
        try:
            assert self.clickcounter == 0 or time.time() - self.timer > 30
            print("Stopwatch:", time.time() - self.timer)
            return DesperateGround(self.button)
        except:
            return SeriousGround(
                self.button, self.word, self.timer, self.cached_artifacts
            )


class DesperateGround(GroundState):
    def __init__(self, button: "Box") -> None:
        self.button = button

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)
        try:
            clicked = self.verify(self.button)
            print(clicked, time.time())
            time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            print("Unexpected error:", e)
            pass

    def next(self) -> GroundState:
        print("Transitioning states...")

        print("Look for whether button moved or disappeared...")
        starttime = time.time()
        while time.time() - starttime < 30:
            try:
                raise Exception  # Implement green checkmark locator here
            except:
                try:
                    clicked = self.redundantclick(self.button)
                    print(clicked, time.time())
                    time.sleep(random.uniform(0.5, 1.5))

                    button = self.findbutton()
                    return FacileGround(button, "puzzle.png")
                except:
                    pass
        print("No button found.")
        return Terminate()


class Terminate(GroundState):
    def run(self) -> None:
        print("State machine terminated.")
        pass

    def next(self) -> None:
        pass


class NotARobot(StateMachine):
    def __init__(self, initialstate: "GroundState" = OpenGround()):
        self.state = initialstate

    def run(self) -> None:
        self.state.run()
        self.state = self.state.next()
        while not isinstance(self.state, Terminate):
            self.state.run()
            self.state = self.state.next()
