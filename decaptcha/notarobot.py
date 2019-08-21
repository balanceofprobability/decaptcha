from decaptcha.base import GroundState
from decaptcha.fsm import StateMachine
from PIL import Image
from pyautogui import locateOnScreen
from pyscreeze import Box
import random
import time
from typing import Dict, List, Optional, Set, Tuple, Union
import os.path


class OpenGround(GroundState):
    """Ground on which each side has liberty of movement is open ground.

    On open ground, do not try to block the enemy's way.
    """

    def __init__(self, killswitch: bool = False):
        self.killswitch = killswitch
        print("!!!! PRINTING FULLPATH !!!!")
        print(self.fullpath)

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        print("Look for robot nazi...")
        try:
            clicked = self.im_not_a_robot()
            print(clicked, time.time())
        except:
            pass

    def next(self) -> GroundState:
        print("Transitioning states...")

        print("Look for grid...")
        starttime = time.time()
        while time.time() - starttime < 10:
            try:
                greencheck = locateOnScreen(
                    os.path.join(self.fullpath, "greencheck.png"), confidence=0.8
                )
                assert hasattr(greencheck, "left")
                print("Victory!")
                return DispersiveGround(victory=True)
            except:
                pass
            try:
                grid = self.find_grid()
                assert grid is not None
                print(grid)
                print("Grid found!")
                return FacileGround(grid)
            except:
                pass

        if self.killswitch == False:
            try:
                print("No grid found. Estimating grid location...")
                print("Look for mr. blue...")
                self.find_mrblue()
                button = self.find_button()
                grid = self.find_grid(button)
                assert grid is not None
                return FacileGround(grid)
            except Exception as e:
                print(e)
                pass

        print("Kill switch triggered.")
        return DispersiveGround(killswitch=True)


class FacileGround(GroundState):
    """When he has penetrated into hostile territory, but to no great distance, it is facile ground.

    On facile ground, halt not.
    """

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
    """Mountain forests, rugged steeps, marshes and fens--all country that is hard to traverse: this is difficult ground.

    In difficult ground, keep steadily on the march.
    """

    def __init__(self, order: List[str] = ["skip.png"]):
        self.order = order
        self.skipped = False

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)
        try:
            # Attempt to locate skip
            button = self.find_button(self.order)
            assert hasattr(button, "left")
            print("Keep steady on the march...")
            clicked = self.attack(button)
            print(clicked, time.time())
            self.skipped = True
            time.sleep(random.uniform(0.5, 1.5))
        except:
            # Attempt to refresh_puzzle
            try:
                print("Locate button...")
                button = self.find_button()
                assert hasattr(button, "left")
                print("Refresh puzzle...")
                clicked = self.refresh_puzzle(button)
                print(clicked, time.time())
                self.clicked = "refresh"
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
                grid = self.find_grid()
                assert grid is not None
                print("Grid found!")
            except:
                pass
            else:
                if self.skipped == True:
                    print("Look for mr. blue...")
                    self.find_mrblue()
                return FacileGround(grid)
        try:
            print("No grid found. Estimating grid location...")
            if self.skipped == True:
                print("Look for mr. blue...")
                self.find_mrblue()
            button = self.find_button()
            assert hasattr(button, "left")
            grid = self.find_grid(button)
            assert grid is not None
            return FacileGround(grid)
        except:
            print("No button found.")
            return OpenGround()


class ContentiousGround(GroundState):
    """Ground the possession of which imports great advantage to either side, is contentious ground.

    On contentious ground, attack not.
    """

    def __init__(self, grid: Tuple[str, int, int, int, int]) -> None:
        self.grid = grid

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        print("extract puzzle_img...")
        wordpuzzle_img, self.puzzle_img = self.extract_puzzle(self.grid)
        print("Puzzle_Img saved!")

        print("Look for stringdump...")
        starttime = time.time()
        while time.time() - starttime < 10:
            try:
                self.word = self.extract_word(wordpuzzle_img).lower()
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
            assert self.is_classifiable(self.word)
            return GroundOfIntersectingHighways(self.grid, self.word, self.puzzle_img)
        except:
            pass
        try:
            assert (
                "select" in self.word
                or "square" in self.word
                or "image" in self.word
                or "verify" in self.word
                or "skip" in self.word
            )
            return DifficultGround()
        except:
            return OpenGround(killswitch=True)


class GroundOfIntersectingHighways(GroundState):
    """Ground which forms the key to three contiguous states, so that he who occupies it first has most of the Empire at his command, is a ground of intersecting highways.

    On the ground of intersecting highways, join hands with your allies.
    """

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
            assert self.grid[0] != "unknown"
            return SeriousGround(self.grid, self.word, self.puzzle_img)
        except:
            return HemmedInGround(self.grid, self.word, self.puzzle_img)


class HemmedInGround(GroundState):
    """Ground which is reached through narrow gorges, and from which we can only retire by tortuous paths, so that a small number of the enemy would suffice to crush a large body of our men: this is hemmed in ground.

    On hemmed-in ground, resort to stratagem.
    """

    def __init__(
        self, grid: Tuple[str, int, int, int, int], word: str, puzzle_img: "Image"
    ) -> None:
        self.grid = grid
        self.word = word
        self.puzzle_img = puzzle_img

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        print("Find all things matching word...")
        things = self.extract_things(self.word, self.puzzle_img)

        estimatedgrid = ("4x4", self.grid[1], self.grid[2], self.grid[3], self.grid[4])

        print("Select hits...")
        self.select_things(things, estimatedgrid)

        self.clickcounter = len(things)
        print("Counter:", self.clickcounter)

        self.bluecheck = locateOnScreen(
            os.path.join(self.fullpath, "bluecheck.png"), confidence=0.7
        )

        if self.clickcounter > 0 and self.bluecheck is None:
            print("Await possible regenerated things...")
            time.sleep(random.uniform(5, 10))

        print("extract puzzle_img...")
        wordpuzzle_img, self.puzzle_img = self.extract_puzzle(self.grid, False)
        print("Puzzle_Img saved!")

    def next(self) -> GroundState:
        print("Transitioning states...")
        try:
            assert self.bluecheck is not None
            return DesperateGround(self.puzzle_img)
        except:
            estimatedgrid = (
                "3x3",
                self.grid[1],
                self.grid[2],
                self.grid[3],
                self.grid[4],
            )
            return SeriousGround(estimatedgrid, self.word, self.puzzle_img)


class SeriousGround(GroundState):
    """When an army has penetrated into the heart of a hostile country, leaving a number of fortified cities in its rear, it is serious ground.

    On serious ground, gather in plunder.
    """

    def __init__(
        self, grid: Tuple[str, int, int, int, int], word: str, puzzle_img: "Image"
    ):
        self.grid = grid
        self.word = word
        self.puzzle_img = puzzle_img
        self.clickcounter = 0

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        things = list()  # type: list

        print("Find all things matching word...")
        things = self.extract_things(self.word, self.puzzle_img)

        print("Select what looks new...")
        self.select_things(things, self.grid)

        self.clickcounter = len(things)
        print("Counter:", self.clickcounter)

        self.bluecheck = locateOnScreen(
            os.path.join(self.fullpath, "bluecheck.png"), confidence=0.7
        )

        if self.clickcounter > 0 and self.bluecheck is None:
            print("Await possible regenerated things...")
            time.sleep(random.uniform(5, 10))

        print("extract puzzle_img...")
        wordpuzzle_img, self.puzzle_img = self.extract_puzzle(self.grid, False)
        print("Puzzle_Img saved!")

    def next(self) -> GroundState:
        print("Transitioning states...")
        try:
            assert self.clickcounter == 0 or self.bluecheck is not None
            return DesperateGround(self.puzzle_img)
        except:
            return SeriousGround(self.grid, self.word, self.puzzle_img)


class DesperateGround(GroundState):
    """Ground on which we can only be saved from destruction by fighting without delay, is desperate ground.

    On desperate ground, fight.
    """

    def __init__(
        self,
        puzzle_img: Optional["Image"] = None,
        order: List[str] = ["verify.png", "next.png"],
    ):
        self.puzzle_img = puzzle_img
        self.order = order

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)
        try:
            button = self.find_button(self.order)
            assert hasattr(button, "left")
            print("Fight!")
            clicked = self.attack(button)
            print(clicked, time.time())
            time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            print("Unexpected error:", e)
            pass

    def next(self) -> GroundState:
        print("Transitioning states...")

        print("Look for grid...")
        starttime = time.time()
        while time.time() - starttime < 10:
            try:
                greencheck = locateOnScreen(
                    os.path.join(self.fullpath, "greencheck.png"), confidence=0.8
                )
                assert hasattr(greencheck, "left")
                print("Victory!")
                return DispersiveGround(victory=True)
            except:
                pass
            try:
                grid = self.find_grid()
                assert grid is not None
                print("Grid found!")
            except:
                pass
            else:
                print("Look for mr. blue...")
                self.find_mrblue()
                return FacileGround(grid, self.puzzle_img)
        try:
            print("No grid found. Estimating grid location...")
            print("Look for mr. blue...")
            self.find_mrblue()
            button = self.find_button()
            grid = self.find_grid(button)
            assert grid is not None
            return FacileGround(grid, self.puzzle_img)
        except:
            print("No button found.")
            return OpenGround()


class DispersiveGround(GroundState):
    """When a chieftain is fighting in his own territory, it is dispersive ground.

    On dispersive ground, therefore, fight not.
    """

    def __init__(self, victory: bool = False, killswitch: bool = False):
        self.victory = victory
        self.killswitch = killswitch

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)
        pass

    def next(self) -> None:
        pass


class NotARobot(StateMachine):
    """The supreme art of war is to subdue the enemy without fighting."""

    def __init__(self):
        self.state = OpenGround()  # type: "GroundState"

    def run(self) -> None:
        self.state.run()
        self.state = self.state.next()
        while not isinstance(self.state, DispersiveGround):
            self.state.run()
            self.state = self.state.next()

    def set_model(self, model_path: str):
        self.state.set_model(model_path)

    def reset(self) -> None:
        self.state = OpenGround()
