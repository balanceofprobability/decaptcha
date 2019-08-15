from decaptcha.base import GroundState
from decaptcha.fsm import StateMachine
from decaptcha.capture import capture
from decaptcha.humanclick import humanclick
from decaptcha.ocr import ocr
from decaptcha.objectdetection import *
from os import getcwd
from PIL import Image
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

        print("Look for grid...")
        starttime = time.time()
        while time.time() - starttime < 30:
            try:
                grid = self.findgrid()
                assert grid is not None
                print(grid)
                print("Grid found!")
                return FacileGround(grid)
            except:
                pass

        try:
            print("No grid found. Estimating grid location...")
            button = self.findbutton()
            grid = self.findgrid(button)
            assert grid is not None
            return FacileGround(grid)
        except:
            print("No button found.")
            return DispersiveGround()


class FacileGround(GroundState):
    def __init__(
        self, grid: Tuple[str, int, int, int, int], cached_puzzle_img: "Image" = None
    ) -> None:
        self.grid = grid
        self.cached_puzzle_img = cached_puzzle_img

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

    def next(self) -> GroundState:
        print("Transitioning states...")
        try:
            print("Attempt to locate cached puzzle_img...")
            self.cached_puzzle_img.save("puzzle.png")  # type: ignore
            cached_puzzle_loc = locateOnScreen("puzzle.png", confidence=0.6)
            assert hasattr(cached_puzzle_loc, "left")
            print("Cached puzzle found!")
            return DifficultGround()
        except:
            print("No cached puzzle_img found...")
            return ContentiousGround(self.grid)


class DifficultGround(GroundState):
    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        try:
            print("Look for mr. blue...")
            mrblue = self.findmrblue()
            self.redundantclick(mrblue)
            print("Locate button...")
            button = self.findbutton()
            print("Refresh puzzle...")
            clicked = self.refreshpuzzle(button)
            print(clicked, time.time())
            time.sleep(random.uniform(4.5, 5.5))
        except Exception as e:
            print(e)
            pass

    def next(self) -> GroundState:
        print("Transitioning states...")

        print("Look for grid...")
        starttime = time.time()
        while time.time() - starttime < 10:
            try:
                grid = self.findgrid()
                assert grid is not None
                print("Grid found!")
                return FacileGround(grid)
            except:
                pass
        try:
            print("No grid found. Estimating grid location...")
            button = self.findbutton()
            grid = self.findgrid(button)
            assert grid is not None
            return FacileGround(grid)
        except:
            print("No button found.")
            return DispersiveGround()


class ContentiousGround(GroundState):
    def __init__(self, grid: Tuple[str, int, int, int, int]) -> None:
        self.grid = grid

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        print("extract puzzle_img...")
        wordpuzzle_img, self.puzzle_img = self.extractpuzzle(self.grid)
        print("Puzzle_Img saved!")

        print("Look for stringdump...")
        starttime = time.time()
        while time.time() - starttime < 10:
            try:
                self.word = self.extractword(wordpuzzle_img)
                print("Stringdump:", self.word)
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
            return GroundOfIntersectingHighways(self.grid, self.word, self.puzzle_img)
        except:
            return DesperateGround(self.puzzle_img)


class GroundOfIntersectingHighways(GroundState):
    def __init__(
        self, grid: Tuple[str, int, int, int, int], word: str, puzzle_img: "Image"
    ) -> None:
        self.grid = grid
        self.word = word
        self.puzzle_img = puzzle_img

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

    def next(self) -> GroundState:
        print("Transitioning states...")

        print("Grid type:", self.grid[0])
        try:
            assert self.grid[0] == "4x4"
            return HemmedInGround(self.grid, self.word, self.puzzle_img)
        except:
            return SeriousGround(self.grid, self.word, self.puzzle_img, time.time())


class HemmedInGround(GroundState):
    def __init__(
        self, grid: Tuple[str, int, int, int, int], word: str, puzzle_img: "Image"
    ) -> None:
        self.grid = grid
        self.word = word
        self.puzzle_img = puzzle_img

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        try:
            print("Find all artifacts matching word...")
            artifacts = self.extractartifacts(self.word, self.puzzle_img)

            print("Select hits...")
            self.selectartifacts(artifacts, self.grid)
        except:
            pass

        print("extract puzzle_img...")
        wordpuzzle_img, self.puzzle_img = self.extractpuzzle(self.grid, False)
        print("Puzzle_Img saved!")

    def next(self) -> GroundState:
        print("Transitioning states...")
        return DesperateGround(self.puzzle_img)


class SeriousGround(GroundState):
    def __init__(
        self,
        grid: Tuple[str, int, int, int, int],
        word: str,
        puzzle_img: "Image",
        timer: float,
    ):
        self.grid = grid
        self.word = word
        self.puzzle_img = puzzle_img
        self.timer = timer
        self.clickcounter = 0

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        artifacts = dict()  # type: dict

        print("Find all artifacts matching word...")
        artifacts = self.extractartifacts(self.word, self.puzzle_img)

        print("Select what looks new...")
        self.selectartifacts(artifacts, self.grid)

        self.clickcounter = len(artifacts)
        print("Counter:", self.clickcounter)

        if (
            self.clickcounter > 0
            and locateOnScreen("decaptcha/bluecheck.png", confidence=0.7) is None
        ):
            print("Await possible regenerated artifacts...")
            time.sleep(random.uniform(5, 10))

        print("extract puzzle_img...")
        wordpuzzle_img, self.puzzle_img = self.extractpuzzle(self.grid, False)
        print("Puzzle_Img saved!")

    def next(self) -> GroundState:
        print("Transitioning states...")
        try:
            assert (
                self.clickcounter == 0
                or time.time() - self.timer > 30
                or locateOnScreen("decaptcha/bluecheck.png", confidence=0.7) is not None
            )
            print("Stopwatch:", time.time() - self.timer)
            return DesperateGround(self.puzzle_img)
        except:
            if self.grid[0] == "unknown":
                print("Look for grid...")
                starttime = time.time()
                while time.time() - starttime < 30:
                    try:
                        grid = self.findgrid()
                        assert grid is not None
                        print(grid)
                        print("Grid found!")
                        return SeriousGround(
                            grid, self.word, self.puzzle_img, self.timer
                        )
                    except:
                        pass

                try:
                    print("No grid found. Estimating grid location...")
                    print("Look for mr. blue...")
                    mrblue = self.findmrblue()
                    self.redundantclick(mrblue)
                    button = self.findbutton()
                    grid = self.findgrid(button)
                    assert grid is not None
                    self.grid = grid
                    print("Updated grid")
                except:
                    print("No button found.")
            return SeriousGround(self.grid, self.word, self.puzzle_img, self.timer)


class DesperateGround(GroundState):
    def __init__(self, puzzle_img: Optional["Image"] = None):
        self.puzzle_img = puzzle_img

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)
        try:
            print("Look for mr. blue...")
            mrblue = self.findmrblue()
            self.redundantclick(mrblue)
            print("Fight!")
            button = self.findbutton()
            clicked = self.attack(button)
            print(clicked, time.time())
            time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            print("Unexpected error:", e)
            pass

    def next(self) -> GroundState:
        print("Transitioning states...")

        try:
            print("Look for mr. blue...")
            mrblue = self.findmrblue()
            self.redundantclick(mrblue)
        except:
            print("No mr. blue.")
            pass

        print("Look for grid...")
        starttime = time.time()
        while time.time() - starttime < 30:
            try:
                greencheck = locateOnScreen("decaptcha/greencheck.png", confidence=0.8)
                assert hasattr(greencheck, "left")
                print("Victory!")
                return DispersiveGround(True)
            except:
                pass
            try:
                grid = self.findgrid()
                assert grid is not None
                print("Grid found!")
                return FacileGround(grid, self.puzzle_img)
            except:
                pass
        try:
            print("No grid found. Estimating grid location...")
            button = self.findbutton()
            grid = self.findgrid(button)
            assert grid is not None
            return FacileGround(grid, self.puzzle_img)
        except:
            print("No button found.")
            return DispersiveGround()


class DispersiveGround(GroundState):
    def __init__(self, victory: bool = False):
        self.victory = victory

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)
        pass

    def next(self) -> None:
        pass


class NotARobot(StateMachine):
    def __init__(self):
        self.state = OpenGround()

    def run(self) -> None:
        self.state.run()
        self.state = self.state.next()
        while not isinstance(self.state, DispersiveGround):
            self.state.run()
            self.state = self.state.next()

    def reset(self) -> None:
        self.state = OpenGround()