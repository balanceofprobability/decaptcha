import math
import os.path
import random
import time
from typing import Dict, List, Optional, Set, Tuple, Union

import PIL.ImageOps
import pyscreenshot as ImageGrab
from PIL import Image, ImageChops
from pyautogui import keyDown, keyUp, locate, locateOnScreen, press
from pyscreeze import Box

from decaptcha.fsm import State, StateMachine
from decaptcha.humanclick import human_click
from decaptcha.imgai import ImgAI
from decaptcha.ocr import ocr


class GroundState(State):
    imgai = ImgAI()
    fullpath = os.path.abspath(os.path.dirname(__file__))
    imnotarobot_img = Image.open(os.path.join(fullpath, "imnotarobot.png"))
    greencheck_img = Image.open(os.path.join(fullpath, "greencheck.png"))
    skip_img = Image.open(os.path.join(fullpath, "skip.png"))
    verify_img = Image.open(os.path.join(fullpath, "verify.png"))
    next_img = Image.open(os.path.join(fullpath, "next.png"))
    grid4x4_img = Image.open(os.path.join(fullpath, "grid4x4.png"))
    grid3x3_img = Image.open(os.path.join(fullpath, "grid3x3.png"))
    bluecheck_img = Image.open(os.path.join(fullpath, "bluecheck.png"))

    def find_puzzle(self, view: Image) -> Tuple[Optional["Box"], str, int]:
        """evaluate if puzzle image is 4x4 or 3x3."""
        grid3x3 = set()  # type: set
        grid4x4 = set()  # type: set
        for confidence in range(60, 30, -10):
            rv = locate(self.grid3x3_img, view, confidence=confidence / 100)
            if rv is not None:
                return rv, "3x3", confidence
            rv = locate(self.grid4x4_img, view, confidence=confidence / 100)
            if rv is not None:
                return rv, "4x4", confidence
        return None, "", confidence

    def find_robot_nazi(self, view: Image) -> Optional[Box]:
        # Locate "I'm not a robot" button on-screen
        return locate(self.imnotarobot_img, view, confidence=0.6)

    def find_greencheck(self, view: Image) -> Optional[Box]:
        # Locate green checkmark on-screen
        return locate(self.greencheck_img, view, confidence=0.8)

    def find_bluecheck(self, view: Image) -> Optional[Box]:
        # Locate green checkmark on-screen
        return locate(self.bluecheck_img, view, confidence=0.7)

    def find_button(
        self, view: Image, order: List["Image"] = [skip_img, verify_img, next_img]
    ) -> Optional[Box]:
        """Locate verify or skip button."""
        for target in order:
            button = locate(target, view, confidence=0.7)
            if button is not None:
                return button
        return None

    def find_cached_puzzle(
        self, cached_puzzle_img: Image, view: Image
    ) -> Optional[Box]:
        return locate(cached_puzzle_img, view, confidence=0.6)

    def estimate_puzzle_loc(self, button: Box, view: Image) -> Box:
        """Estimate puzzle frame location on-screen using button as reference."""
        # Compute coordinate references
        if button is not None:
            box_top = int(button.top - 552 + (button.height + button.height) / 2)
            box_left = int(button.left - 342 + (button.height + button.height) / 2)
            return Box(box_left, box_top, 400, 520)
        else:
            return None

    def shift_tab(self) -> None:
        """Move focus w/ shift-tab"""
        keyDown("shift")
        press("tab")
        keyUp("shift")

    def refresh_puzzle(self, button: Box) -> Tuple[int, int]:
        left = int(button.left - 325 + (button.width + button.width) / 2)
        top = int(button.top - 10 + (button.height + button.height) / 2)
        right = left + 20
        bottom = top + 20
        return human_click(left, top, right, bottom)

    def extract_fullpuzzle(
        self, puzzle_frame: Box, view: Image, y_offset: int = -31
    ) -> Tuple[Optional["Image"], Optional["Image"]]:
        """Screenshot word & puzzle region, based on puzzle_frame location on-screen"""
        return view.crop(
            (
                puzzle_frame.left,
                puzzle_frame.top + y_offset,
                puzzle_frame.left + puzzle_frame.width,
                puzzle_frame.top + 121 + 400 + y_offset,
            )
        )

    def extract_puzzle(
        self, puzzle_frame: Box, view: Image, y_offset: int = -31
    ) -> Tuple[Optional["Image"], Optional["Image"]]:
        """Screenshot word & puzzle region, based on puzzle_frame location on-screen"""
        return view.crop(
            (
                puzzle_frame.left,
                puzzle_frame.top + 121 + y_offset,
                puzzle_frame.left + puzzle_frame.width,
                puzzle_frame.top + 121 + 400 + y_offset,
            )
        )

    def extract_wordpuzzle(
        self, puzzle_frame: Box, view: Image, y_offset: int = -31
    ) -> Tuple[Optional["Image"], Optional["Image"]]:
        """Screenshot word & puzzle region, based on puzzle_frame location on-screen"""
        return view.crop(
            (
                puzzle_frame.left,
                puzzle_frame.top + y_offset,
                puzzle_frame.left + puzzle_frame.width,
                puzzle_frame.top + 121 + y_offset,
            )
        )

    def extract_word(self, wordpuzzle_img: Image) -> str:
        """Extract word(s), given puzzle image"""
        if wordpuzzle_img.mode == "RGBA":
            r, g, b, a = wordpuzzle_img.split()
            rgb_img = Image.merge("RGB", (r, g, b))
            wordpuzzle_img_invert = PIL.ImageOps.invert(rgb_img)
        else:
            wordpuzzle_img_invert = PIL.ImageOps.invert(wordpuzzle_img)

        wordpuzzle_img_invert_grey = wordpuzzle_img_invert.convert("L")

        words_img = wordpuzzle_img_invert_grey.resize(
            (4 * wordpuzzle_img.width, 4 * wordpuzzle_img.height), Image.LANCZOS
        )
        return ocr(words_img, 0, 0, words_img.width, words_img.height)  # type: ignore

    def attack(self, button: Box) -> Tuple[int, int]:
        """Click button, albeit 'skip', 'verify', or 'next'"""
        left = int(button.left + 0.2 * button.width)
        top = int(button.top + 0.2 * button.height)
        right = int(button.left + 0.8 * button.width)
        bottom = int(button.top + 0.8 * button.height)
        return human_click(left, top, right, bottom)

    def select_things(
        self, things: List[Tuple[int, int, int, int]], puzzle_frame: Box, grid_type: str
    ) -> None:
        """Click on all things, relative to button location.

        If grid parameter specified, click on all grid cells occupied by any things.

        INPUT
        -----
        cached_things : dict()
        """

        # Constant parameters
        puzzle_offset_y = 120
        click_margin_x = 5
        click_margin_y = 35

        # Constant parameters
        n, m = int(grid_type[0]), int(grid_type[2])
        grid_margin_x, grid_margin_y = self.grid_margins(n, m)
        cell_width, cell_height = self.cell_dimensions(
            puzzle_frame.width, puzzle_frame.height, grid_margin_x, grid_margin_y, n, m
        )

        # Iterate through cells in nxn grid and click it if occupied by an thing
        for cell in range(n * m):

            # Define cell as row & col no.
            row, col = self.nxm(n, m, cell)

            # Calculate cell region relative to puzzle coordinates
            cell_left = col * cell_width + grid_margin_x
            cell_top = row * cell_width + grid_margin_y
            cell_right = (col + 1) * cell_width + grid_margin_x
            cell_bottom = (row + 1) * cell_width + grid_margin_y

            # Determine whether cell region contains an thing
            for thing in things:

                try:
                    # Check if a collision occurs
                    assert (
                        # Collision in x axis
                        self.is_collision(
                            tuple([thing[0], thing[2]]),  # type: ignore
                            tuple([cell_left, cell_right]),  # type: ignore
                        )
                        # Collision in y axis
                        and self.is_collision(
                            tuple([thing[1], thing[3]]),  # type: ignore
                            tuple([cell_top, cell_bottom]),  # type: ignore
                        )
                    )

                except:
                    # No collision here
                    pass

                else:
                    if grid_type == "3x3":
                        # if center of thing is in cell, append collision size to cell_buffer
                        try:
                            x_ctr = (thing[0] + thing[2]) / 2
                            y_ctr = (thing[1] + thing[3]) / 2
                            assert (
                                x_ctr > cell_left
                                and x_ctr < cell_right
                                and y_ctr > cell_top
                                and y_ctr < cell_bottom
                            )

                            # Click within cell region & proceed to next cell
                            left = puzzle_frame.left + cell_left + click_margin_x
                            top = (
                                puzzle_frame.top
                                + cell_top
                                + puzzle_offset_y
                                + click_margin_y
                            )
                            right = puzzle_frame.left + cell_right - click_margin_x
                            bottom = (
                                puzzle_frame.top
                                + cell_bottom
                                + puzzle_offset_y
                                - click_margin_y
                            )

                            clicked = human_click(left, top, right, bottom)
                            print(clicked, time.time())
                            break
                        except:
                            pass
                    else:
                        # Click within cell region & proceed to next cell
                        left = puzzle_frame.left + cell_left + click_margin_x
                        top = (
                            puzzle_frame.top
                            + cell_top
                            + puzzle_offset_y
                            + click_margin_y
                        )
                        right = puzzle_frame.left + cell_right - click_margin_x
                        bottom = (
                            puzzle_frame.top
                            + cell_bottom
                            + puzzle_offset_y
                            - click_margin_y
                        )

                        clicked = human_click(left, top, right, bottom)
                        print(clicked, time.time())
                        break

    #### Class Methods ####
    @classmethod
    def set_model(cls, model_path: str) -> None:
        cls.imgai.set_model(model_path)

    @classmethod
    def is_classifiable(cls, word: str) -> bool:
        for thing in cls.imgai.object_lib():
            if thing in word:
                return True
        return False

    @classmethod
    def extract_things(
        cls, word: str, puzzle_img: Image
    ) -> List[Tuple[int, int, int, int]]:
        """Find all things that match word in last saved puzzle and save as images
        Return a dictionary of things containing relative coordinates hashed by their filenames

        INPUT
        -----
        word : str

        puzzle_img : Image
        """

        # Detect things in last saved puzzle
        puzzle_img.save("puzzle.png")
        detections = cls.imgai.object_detector(word, "puzzle.png")  # type: List
        assert isinstance(detections, list)

        # Iterate through detections and parse the things...
        result = list()  # type: list
        for thing in detections:
            # Append all "box_points" to result
            result.append(thing["box_points"])
        return result

    #### Pure functions ####
    @staticmethod
    def invert_img(img: Image) -> Image:
        if img.mode == "RGBA":
            r, g, b, a = img.split()
            rgb_img = Image.merge("RGB", (r, g, b))
            invert_rgb_img = PIL.ImageOps.invert(rgb_img)
            r_i, g_i, b_i = invert_rgb_img.split()
            invert_rgba_img = Image.merge("RGBA", (r_i, g_i, b_i, a))
            return invert_rgba_img
        else:
            invert_img = PIL.ImageOps.invert(img)
            return invert_img

    @staticmethod
    def is_collision(edge1: Tuple[int, int], edge2: Tuple[int, int]) -> bool:
        """Takes two collinear edges and returns True if they overlap"""
        if (
            edge1[0] > edge2[0]
            and edge1[0] < edge2[1]
            or edge1[1] > edge2[0]
            and edge1[1] < edge2[1]
            or edge2[0] > edge1[0]
            and edge2[0] < edge1[1]
            or edge2[1] > edge1[0]
            and edge2[1] < edge1[1]
        ):
            return True
        else:
            return False

    @staticmethod
    def nxm(n: int, m: int, cell: int) -> Tuple[int, int]:
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

    @staticmethod
    def grid_margins(n: int, m: int) -> Tuple[int, int]:
        """Adhoc solution to parametrically calculate the appropriate grid margins, given the number of rows and columns in the grids nxm matrix

        Note: not designed for any nxm matrices that are not 4x4 and 3x3
        """
        return 5 + n % 3, 5 + m % 3

    @staticmethod
    def cell_dimensions(
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

    @staticmethod
    def rms_diff(img1: Image, img2: Image) -> float:
        "Calculate the root-mean-square difference between two images"
        if img1.mode != "RGB":
            img1.convert("RGB")
        if img2.mode != "RGB":
            img2.convert("RGB")
        diff = ImageChops.difference(img1, img2)
        h = diff.histogram()
        sq = (value * ((idx % 256) ** 2) for idx, value in enumerate(h))
        sum_of_squares = sum(sq)
        rms = math.sqrt(sum_of_squares / float(img1.size[0] * img1.size[1]))
        return rms
