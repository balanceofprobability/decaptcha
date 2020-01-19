import random
import time
from typing import List, Optional, Tuple

import pyscreenshot as ImageGrab
from decaptcha.base import GroundState
from decaptcha.fsm import StateMachine
from decaptcha.humanclick import human_click
from PIL import Image
from pyautogui import locate
from pyscreeze import Box


class OpenGround(GroundState):
    """Ground on which each side has liberty of movement is open ground.

    On open ground, do not try to block the enemy's way.
    """

    def __init__(self, cached_puzzle_img: Optional["Image"] = None):
        self.cached_puzzle_img = cached_puzzle_img

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)
        self.view = ImageGrab.grab()
        self.grid = self.find_grid(self.view)
        self.robot_nazi = self.find_robot_nazi(self.view) if self.grid is None else None
        self.victory = True if self.find_greencheck(self.view) is not None else False
        self.button = (
            self.find_button(self.view)
            if self.grid is None and self.robot_nazi is None
            else None
        )
        print(
            "grid:",
            self.grid,
            "\nrobot nazi:",
            self.robot_nazi,
            "\nvictory:",
            self.victory,
        )

    def next(self) -> GroundState:
        print("Transitioning states...")

        if self.grid is not None or self.button is not None:
            return (
                ContentiousGround(self.grid, self.cached_puzzle_img)
                if self.grid is not None
                else ContentiousGround(
                    self.find_grid(self.view, self.button), self.cached_puzzle_img
                )
            )
        elif self.robot_nazi is not None and self.victory is False:
            return FacileGround(self.cached_puzzle_img)
        elif self.victory == True:
            print("The supreme art of war is to subdue the enemy without fighting.")
        else:
            print(
                "".join(
                    [
                        "It is possible to commit no mistakes and still lose. ",
                        "That is not a weakness; that is life.",
                    ]
                )
            )
        return DispersiveGround(self.victory)


class DispersiveGround(GroundState):
    """When a chieftain is fighting in his own territory, it is dispersive ground.

    On dispersive ground, therefore, fight not.
    """

    def __init__(self, victory: bool):
        self.victory = victory

    def run(self) -> None:
        pass

    def next(self) -> None:
        pass


class FacileGround(GroundState):
    """When he has penetrated into hostile territory, but to no great distance, it is facile ground.

    On facile ground, halt not.
    """

    def __init__(
        self, cached_puzzle_img: Optional["Image"] = None, timeout: int = 10,
    ) -> None:
        self.cached_puzzle_img = cached_puzzle_img
        self.timeout = timeout

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)
        robot_nazi = self.find_robot_nazi(ImageGrab.grab())
        if robot_nazi is not None:
            # Click "I'm not a robot" button like a human
            left = int(robot_nazi.left + 0.20 * robot_nazi.width)
            top = int(robot_nazi.top + 0.20 * robot_nazi.height)
            right = int(robot_nazi.left + 0.75 * robot_nazi.width)
            bottom = int(robot_nazi.top + 0.80 * robot_nazi.height)
            clicked = human_click(left, top, right, bottom)  # type: ignore
            print(clicked, time.time())
        starttime = time.time()
        while time.time() - starttime < self.timeout:
            view = ImageGrab.grab()
            grid_buffer = self.find_grid(view)
            self.grid = (
                grid_buffer
                if grid_buffer is not None
                else self.find_grid(view, self.find_button(view))
            )
            if self.grid is not None:
                break

    def next(self) -> GroundState:
        print("Transitioning states...")

        if self.grid is not None:
            print("Found grid!")
            return ContentiousGround(self.grid, self.cached_puzzle_img)
        else:
            print("No grid found...")
            return OpenGround(self.cached_puzzle_img)


class ContentiousGround(GroundState):
    """Ground the possession of which imports great advantage to either side, is contentious ground.

    On contentious ground, attack not.
    """

    def __init__(
        self,
        grid: Optional[Tuple[str, int, int, int, int]],
        cached_puzzle_img: Optional["Image"] = None,
    ) -> None:
        self.grid = grid
        self.cached_puzzle_img = cached_puzzle_img

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        print("Attempt to locate cached puzzle_img...")
        self.cached_puzzle = (
            locate(self.cached_puzzle_img, ImageGrab.grab(), confidence=0.6)
            if self.cached_puzzle_img is not None
            else None
        )

    def next(self) -> GroundState:
        print("Transitioning states...")

        if self.grid is None:
            print("Lost grid...")
            return OpenGround(self.cached_puzzle_img)
        elif self.cached_puzzle is not None:
            print("Cached puzzle found!")
            return DifficultGround()
        else:
            print("No cached puzzle image found...")
            return GroundOfIntersectingHighways(self.grid)


class GroundOfIntersectingHighways(GroundState):
    """Ground which forms the key to three contiguous states, so that he who occupies it first has most of the Empire at his command, is a ground of intersecting highways.

    On the ground of intersecting highways, join hands with your allies.
    """

    def __init__(self, grid: Tuple[str, int, int, int, int], timeout: int = 10) -> None:
        self.grid = grid
        self.timeout = timeout

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        print("extract puzzle_img...")
        wordpuzzle_img, self.puzzle_img = self.extract_puzzle(self.grid)
        print("Look for stringdump...")
        starttime = time.time()
        while time.time() - starttime < self.timeout:
            self.stringdump = self.extract_word(wordpuzzle_img).lower()
            print("Stringdump:", self.stringdump)
            if "vehicles" in self.stringdump:
                self.stringdump = "carsbusmotorcycles"
            if len(self.stringdump) > 0:
                break
        self.isclassifiable = self.is_classifiable(self.stringdump)

    def next(self) -> GroundState:
        print("Transitioning states...")

        print("Grid type:", self.grid[0])
        if self.grid[0] != "unknown" and self.isclassifiable == True:
            return SeriousGround(self.grid, self.stringdump, self.puzzle_img)
        elif self.isclassifiable == True:
            return HemmedInGround(self.grid, self.stringdump, self.puzzle_img)
        else:
            return DifficultGround()


class DifficultGround(GroundState):
    """Mountain forests, rugged steeps, marshes and fens--all country that is hard to traverse: this is difficult ground.

    In difficult ground, keep steadily on the march.
    """

    def __init__(self, order: List[str] = [GroundState.skip_img], timeout: int = 10):
        self.order = order
        self.timeout = timeout
        self.skipped = False

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)
        # Attempt to locate skip
        view = ImageGrab.grab()
        try:
            button = self.find_button(view, self.order)
            print("Keep steady on the march...")
            clicked = self.attack(button)
            self.skipped = True
            print(clicked, time.time())
            time.sleep(random.uniform(0.5, 1.5))
        except:
            button = self.find_button(view)
            # Attempt to refresh_puzzle
            print("Refresh puzzle...")
            if button is not None:
                clicked = self.refresh_puzzle(button)
                print(clicked, time.time())
                time.sleep(random.uniform(4.5, 5.5))

    def next(self) -> GroundState:
        print("Transitioning states...")

        print("Look for grid...")
        starttime = time.time()
        while time.time() - starttime < self.timeout:
            self.grid = self.find_grid(ImageGrab.grab())
            if self.grid is not None:
                break
        if self.skipped == True:
            self.shift_tab()
        return ContentiousGround(self.grid) if self.grid is not None else OpenGround()


class HemmedInGround(GroundState):
    """Ground which is reached through narrow gorges, and from which we can only retire by tortuous paths, so that a small number of the enemy would suffice to crush a large body of our men: this is hemmed in ground.

    On hemmed-in ground, resort to stratagem.
    """

    def __init__(
        self, grid: Tuple[str, int, int, int, int], word: str, puzzle_img: Image
    ) -> None:
        self.grid = grid
        self.stringdump = word
        self.puzzle_img = puzzle_img

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        print("Find all things matching word...")
        things = self.extract_things(self.stringdump, self.puzzle_img)

        estimatedgrid = ("4x4", self.grid[1], self.grid[2], self.grid[3], self.grid[4])

        print("Select hits...")
        self.select_things(things, estimatedgrid)

        self.thing_counter = len(things)
        print("Counter:", self.thing_counter)

        self.bluecheck = locate(self.bluecheck_img, ImageGrab.grab(), confidence=0.7)

        if self.thing_counter > 0 and self.bluecheck is None:
            print("Await possible regenerated things...")
            time.sleep(random.uniform(5, 10))

        print("extract puzzle_img...")
        self.puzzle_img = self.extract_puzzle(self.grid, False)[1]
        print("Puzzle_Img saved!")

    def next(self) -> GroundState:
        print("Transitioning states...")
        if self.bluecheck is None:
            return DesperateGround(self.puzzle_img)
        else:
            estimatedgrid = (
                "3x3",
                self.grid[1],
                self.grid[2],
                self.grid[3],
                self.grid[4],
            )
            return SeriousGround(estimatedgrid, self.stringdump, self.puzzle_img)


class SeriousGround(GroundState):
    """When an army has penetrated into the heart of a hostile country, leaving a number of fortified cities in its rear, it is serious ground.

    On serious ground, gather in plunder.
    """

    def __init__(
        self,
        grid: Tuple[str, int, int, int, int],
        word: str,
        puzzle_img: Image,
        timeout: int = 10,
    ):
        self.grid = grid
        self.stringdump = word
        self.puzzle_img = puzzle_img
        self.thing_counter = 0
        self.timeout = timeout

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)

        things = list()  # type: list

        print("Find all things matching word...")
        things = self.extract_things(self.stringdump, self.puzzle_img)

        print("Select what looks new...")
        self.select_things(things, self.grid)

        cached_puzzle_img = self.extract_puzzle(self.grid, False)[1]

        self.thing_counter = len(things)
        print("Counter:", self.thing_counter)

        self.bluecheck = locate(self.bluecheck_img, ImageGrab.grab(), confidence=0.7)

        if self.thing_counter > 0 and self.bluecheck is None:
            print("Await possible regenerated things...")
            timer = time.time()
            while time.time() - timer < self.timeout:
                self.puzzle_img = self.extract_puzzle(self.grid, False)[1]
                rms = self.rms_diff(cached_puzzle_img, self.puzzle_img)
                if rms < 20:
                    print("Nothing's changed. Move along!", rms, time.time() - timer)
                    break
                print(rms, time.time() - timer)
                cached_puzzle_img = self.extract_puzzle(self.grid, False)[1]
                time.sleep(random.uniform(0.5, 1))
        else:
            self.puzzle_img = cached_puzzle_img

    def next(self) -> GroundState:
        print("Transitioning states...")
        if self.thing_counter == 0 or self.bluecheck is not None:
            return DesperateGround(self.puzzle_img)
        else:
            return SeriousGround(self.grid, self.stringdump, self.puzzle_img)


class DesperateGround(GroundState):
    """Ground on which we can only be saved from destruction by fighting without delay, is desperate ground.

    On desperate ground, fight.
    """

    def __init__(
        self,
        cached_puzzle_img: Optional["Image"] = None,
        order: List[str] = [GroundState.verify_img, GroundState.next_img],
    ):
        self.cached_puzzle_img = cached_puzzle_img
        self.order = order

    def run(self) -> None:
        print("\nEntered", self.__class__.__name__)
        button = self.find_button(ImageGrab.grab(), self.order)
        if button is not None:
            print("Fight!")
            clicked = self.attack(button)
            self.shift_tab()
            print(clicked, time.time())
            time.sleep(random.uniform(0.5, 1.5))

    def next(self) -> GroundState:
        print("Transitioning states...")

        return OpenGround(self.cached_puzzle_img)


class NotARobot(StateMachine):
    """The supreme art of war is to subdue the enemy without fighting."""

    def __init__(self, initial_state=OpenGround()):
        self.initial_state = initial_state  # type: "GroundState"
        self.state = initial_state  # type: "GroundState"

    def run(self) -> None:
        while not isinstance(self.state, DispersiveGround):
            self.state.run()
            self.state = self.state.next()

    def set_model(self, model_path: str):
        self.state.set_model(model_path)

    def reset(self) -> None:
        self.state = self.initial_state
