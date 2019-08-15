from decaptcha.fsm import State, StateMachine
from decaptcha.capture import capture
from decaptcha.humanclick import humanclick
from decaptcha.ocr import ocr
from decaptcha.objectdetection import *
from os import getcwd
from PIL import Image
import PIL.ImageOps
from pyautogui import locate
from pyautogui import locateOnScreen
import pyscreenshot as ImageGrab
from pyscreeze import Box
import random
import time
from typing import Dict, List, Optional, Set, Tuple, Union


class GroundState(State):
    def imnotarobot(self) -> Tuple[int, int]:
        try:
            # Locate "I'm not a robot" button on screen
            imnotarobot = locateOnScreen("decaptcha/imnotarobot.png", confidence=0.6)
            # Click "I'm not a robot" button like a human
            left = int(imnotarobot.left + 0.20 * imnotarobot.width)
            top = int(imnotarobot.top + 0.20 * imnotarobot.height)
            right = int(imnotarobot.left + 0.75 * imnotarobot.width)
            bottom = int(imnotarobot.top + 0.80 * imnotarobot.height)
            return humanclick(left, top, right, bottom)
        except:
            pass
        raise AttributeError("Failed to locate imnotarobot")

    def findbutton(self) -> "Box":
        # Attempt to see if recaptcha test exists on screen
        # try finding verify or skip button
        for target in ["skip.png", "verify.png", "next.png"]:
            try:
                button = locateOnScreen("".join(["decaptcha/", target]), confidence=0.7)
                assert hasattr(button, "left")
                return button
            except AssertionError:
                pass
        raise AttributeError("Failed to locate button")

    def findmrblue(self) -> "Box":
        # Attempt to see if recaptcha test exists on screen
        # try finding verify or skip button
        try:
            mrblue = locateOnScreen("decaptcha/mrblue.png", confidence=0.7)
            assert hasattr(mrblue, "left")
            return mrblue
        except AssertionError:
            pass
        raise AttributeError("Failed to locate mr. blue")

    def refreshpuzzle(self, button: "Box") -> Tuple[int, int]:
        left = int(button.left) - 325 + int((button.width + button.width % 2) / 2)
        top = int(button.top) - 10 + int((button.height + button.height % 2) / 2)
        right = left + 20
        bottom = top + 20
        return humanclick(left, top, right, bottom)

    def extractpuzzle(
        self,
        grid: Tuple[str, int, int, int, int],
        wordpuzzle: bool = True,
        puzzle: bool = True,
    ) -> Tuple[Optional["Image"], Optional["Image"]]:
        """Screenshot word & puzzle region, based on grid location on-screen"""
        screen = ImageGrab.grab()
        if wordpuzzle == True:
            wordpuzzle_img = screen.crop(
                (grid[1], grid[2], grid[1] + grid[3], grid[2] + 121)
            )
        else:
            wordpuzzle_img = None
        if puzzle == True:
            puzzle_img = screen.crop(
                (grid[1], grid[2] + 121, grid[1] + grid[3], grid[2] + 121 + 400)
            )
        else:
            puzzle_img = None
        return wordpuzzle_img, puzzle_img

    def extractword(self, wordpuzzle_img: "Image") -> str:
        """Extract word(s), given puzzle image"""
        if wordpuzzle_img.mode == "RGBA":
            r, g, b, a = wordpuzzle_img.split()
            rgb_img = Image.merge("RGB", (r, g, b))
            wordpuzzle_img_invert = PIL.ImageOps.invert(rgb_img)
        else:
            wordpuzzle_img_invert = PIL.ImageOps.invert(wordpuzzle_img)

        wordpuzzle_img_invert_grey = wordpuzzle_img_invert.convert("LA")

        words_img = wordpuzzle_img_invert_grey.resize(
            (4 * wordpuzzle_img.width, 4 * wordpuzzle_img.height), Image.ANTIALIAS
        )
        word = ocr(words_img, 0, 0, words_img.width, words_img.height)  # type: ignore

        try:
            assert isinstance(word, str)
        except:
            raise TypeError
        return word

    def isclassifiable(self, word: str) -> bool:
        for thing in objectlib():
            if thing in word:
                return True
        return False

    def attack(self, button: "Box") -> Tuple[int, int]:
        """Click button, albeit 'skip', 'verify', or 'next'"""
        left = int(button.left + 0.2 * button.width)
        top = int(button.top + 0.2 * button.height)
        right = int(button.left + 0.8 * button.width)
        bottom = int(button.top + 0.8 * button.height)
        return humanclick(left, top, right, bottom)

    def redundantclick(self, button: "Box") -> Tuple[int, int]:
        # Click arbitrary spot left of verify
        left = int(button.left) + int(0.2 * button.width)
        top = int(button.top) + int(0.2 * button.height)
        right = int(button.left) + int(0.8 * button.width)
        bottom = int(button.top) + int(0.8 * button.height)
        return humanclick(left, top, right, bottom)

    def extractartifacts(
        self, word: str, puzzle_img: "Image"
    ) -> Dict[str, Tuple[int, int, int, int]]:
        """Find all artifacts that match word in last saved puzzle and save as images
        Return a dictionary of artifacts containing relative coordinates hashed by their filenames

        INPUT
        -----
        word : str

        puzzle_img : "Image"
        """

        # Detect artifacts in last saved puzzle
        puzzle_img.save("puzzle.png")  # type: ignore
        detections = objectdetection(word, "puzzle.png")  # type: List
        assert isinstance(detections, list)

        # Iterate through detections and return saved img names and regions...
        result = dict()  # type: dict
        for thing in detections:

            try:
                # Crop images in puzzle contained within "box_points" & save to filename
                left = int(thing["box_points"][0])
                upper = int(thing["box_points"][1])
                right = int(thing["box_points"][2])
                lower = int(thing["box_points"][3])

                filename = "".join(["L", str(left), "T", str(upper), ".png"])

                img_crop = puzzle_img.crop((left, upper, right, lower))
                img_crop.save(filename)
                img_crop.close()
                img.close()
            except:
                pass
            else:
                result[filename] = thing["box_points"]

        return result

    def findgrid(
        self, button: Optional["Box"] = None
    ) -> Optional[Tuple[str, int, int, int, int]]:
        """locate 4x4 or 3x3 grid on-screen, or estimate its approximate location."""

        if button is None:
            try:
                box = locateOnScreen("decaptcha/white4x4.png", confidence=0.5)
                assert hasattr(box, "left")
                return (
                    "4x4",
                    int(box.left),
                    int(box.top),
                    int(box.width),
                    int(box.height),
                )
            except:
                pass

            try:
                box = locateOnScreen("decaptcha/white3x3.png", confidence=0.5)
                assert hasattr(box, "left")
                return (
                    "3x3",
                    int(box.left),
                    int(box.top),
                    int(box.width),
                    int(box.height),
                )
            except:
                pass

        else:
            try:
                # Guessing enabled. Use button as reference...
                assert hasattr(button, "left")

                # Compute coordinate references
                box_top = (
                    int(button.top)  # type: ignore
                    - 552
                    + int((button.height + button.height % 2) / 2)  # type: ignore
                )
                box_left = (
                    int(button.left)  # type: ignore
                    - 342
                    + int((button.width + button.width % 2) / 2)  # type: ignore
                )

                return ("unknown", box_left, box_top, 400, 520)
            except Exception as e:
                print(e)
                pass

        return None

    def selectartifacts(
        self,
        artifacts: Dict[str, Tuple[int, int, int, int]],
        grid: Tuple[str, int, int, int, int],
    ) -> None:
        """Click on all artifacts, relative to button location.

        If grid parameter specified, click on all grid cells occupied by any artifacts.

        INPUT
        -----
        cached_artifacts : dict()
        """

        # Constant parameters
        puzzle_offset_y = 120
        click_margin_x = 5
        click_margin_y = 30

        # Check for whether nxn grid was identified
        if grid[0] == "4x4" or grid[0] == "3x3":

            # Constant parameters
            n, m = int(grid[0][0]), int(grid[0][2])
            grid_margin_x, grid_margin_y = self.grid_margins(n, m)
            cell_width, cell_height = self.cell_dimensions(
                grid[3], grid[4], grid_margin_x, grid_margin_y, n, m
            )

            # Grid exists. Iterate through cells in nxn grid and click it if occupied by an artifact
            for cell in range(n * m):

                # Define cell as row & col no.
                row, col = self.nxm(n, m, cell)

                # Calculate cell region relative to puzzle coordinates
                cell_left = col * cell_width + grid_margin_x
                cell_top = row * cell_width + grid_margin_y
                cell_right = (col + 1) * cell_width + grid_margin_x
                cell_bottom = (row + 1) * cell_width + grid_margin_y

                # Determine whether cell region contains an artifact
                for artifact in artifacts.values():

                    try:
                        # Check if a collision occurs
                        assert (
                            # Collision in x axis
                            self.iscollision(  # type: ignore
                                tuple([artifact[0], artifact[2]]),
                                tuple([cell_left, cell_right]),
                            )
                            # Collision in y axis
                            and self.iscollision(  # type: ignore
                                tuple([artifact[1], artifact[3]]),
                                tuple([cell_top, cell_bottom]),
                            )
                        )

                    except:
                        # No collision here
                        pass

                    else:
                        # Click within cell region & proceed to next cell
                        left = grid[1] + cell_left + click_margin_x
                        top = grid[2] + cell_top + puzzle_offset_y + click_margin_y
                        right = grid[1] + cell_right - click_margin_x
                        bottom = (
                            grid[2] + cell_bottom + puzzle_offset_y - click_margin_y
                        )

                        clicked = humanclick(left, top, right, bottom)
                        print(clicked, time.time())
                        break

        # No grid specified. Click all artifacts relative to button
        else:
            try:
                for artifact in artifacts.values():
                    left = (
                        artifact[0] + grid[1] + int(0.2 * (artifact[2] - artifact[0]))
                    )
                    top = (
                        artifact[1]
                        + grid[2]
                        + int(0.2 * (artifact[3] - artifact[1]))
                        + puzzle_offset_y
                    )
                    right = (
                        artifact[2] + grid[1] - int(0.2 * (artifact[2] - artifact[0]))
                    )
                    bottom = (
                        artifact[3]
                        + grid[2]
                        - int(0.2 * (artifact[3] - artifact[1]))
                        + puzzle_offset_y
                    )

                    clicked = humanclick(left, top, right, bottom)
                    print(clicked, time.time())
            except:
                pass

    # Pure functions
    def iscollision(self, edge1: Tuple[int, int], edge2: Tuple[int, int]) -> bool:
        """Takes two parallel 1-D edges and returns True if they overlap"""
        if (
            edge1[0] >= edge2[0]
            and edge1[0] <= edge2[1]
            or edge1[1] >= edge2[0]
            and edge1[1] <= edge2[1]
            or edge2[0] >= edge1[0]
            and edge2[0] <= edge1[1]
            or edge2[1] >= edge1[0]
            and edge2[1] <= edge1[1]
        ):
            return True
        else:
            return False

    def nxm(self, n: int, m: int, cell: int) -> Tuple[int, int]:
        """Return the row & column, given the index of a 1-D array representing an nxm matrix.

        INPUT
        -----
        n : int, total number of rows in the nxm matrix

        m : int, total number of columns in the nxm matrix

        cell : int, index of the nxn matrix represented as a 1-D array

        RETURN:
        -------
        Tuple[int, int], row & column number of corresponding cell
        """
        return (int((cell - cell % n) / n)), cell % m

    def grid_margins(self, n: int, m: int) -> Tuple[int, int]:
        """Adhoc solution to parametrically calculate the appropriate grid margins, given the number of rows and columns in the grids nxm matrix

        Note: not designed for any nxm matrices that are not 4x4 and 3x3
        """
        return 5 + n % 3, 5 + m % 3

    def cell_dimensions(
        self,
        grid_width: int,
        grid_height: int,
        grid_margin_x: int,
        grid_margin_y: int,
        n: int,
        m: int,
    ):
        """Return the cell width & height, given the grid width, grid height, cell offset, and number of rows (or columns).

        INPUT
        -----
        grid_width : int, total width of grid (including margins)

        grid_margins : Tuple[int, int], horizontal and vertical offset between edge of grid and its nearest cell

        n : int, number of rows (or columns) in the nxm matrix

        RETURN:
        -------
        Tuple[int, int], row & column number of corresponding cell
        """
        return (
            int((grid_width - 2 * grid_margin_x) / n),
            int((grid_height - 2 * grid_margin_y) / m),
        )
