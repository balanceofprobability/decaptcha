from decaptcha.fsm import State, StateMachine
from decaptcha.capture import capture
from decaptcha.humanclick import humanclick
from decaptcha.ocr import ocr
from decaptcha.objectdetection import *
from os import getcwd
from PIL import Image
from pyautogui import locate
from pyautogui import locateOnScreen
from pyscreeze import Box
import random
import time
from typing import Dict, List, Optional, Set, Tuple, Union


class GroundState(State):
    def imnotarobot(self) -> Tuple[int, int]:
        # Locate "I'm not a robot" button on screen
        imnotarobot = locateOnScreen(
            getcwd() + "/decaptcha/imnotarobot.png", confidence=0.7
        )
        # Click "I'm not a robot" button like a human
        left = int(imnotarobot.left + 0.10 * imnotarobot.width)
        top = int(imnotarobot.top - 0.10 * imnotarobot.height)
        right = int(imnotarobot.left + 0.75 * imnotarobot.width)
        bottom = int(imnotarobot.top + 0.90 * imnotarobot.height)
        return humanclick(left, top, right, bottom)

    def findbutton(self) -> "Box":
        # Attempt to see if recaptcha test exists on screen
        # try finding verify or skip button
        for target in ["skip.png", "verify.png", "next.png"]:
            try:
                button = locateOnScreen(
                    getcwd() + "/decaptcha/" + target, confidence=0.7
                )
                assert isinstance(button, tuple)
                return button
            except AssertionError:
                pass
        raise AttributeError("Failed to locate button")

    def refreshpuzzle(self, button: "Box") -> Tuple[int, int]:
        left = int(button.left) - 325 + int((button.width + button.width % 2) / 2)
        top = int(button.top) - 10 + int((button.height + button.height % 2) / 2)
        right = left + 20
        bottom = top + 20
        return humanclick(left, top, right, bottom)

    def savepuzzle(self, button: "Box", puzzlename: str = "puzzle.png") -> None:
        target_offset_top = (
            button.top - 428 + int((button.height + button.height % 2) / 2)
        )
        target_offset_left = (
            button.left - 342 + int((button.width + button.width % 2) / 2)
        )
        capture(
            target_offset_top,
            target_offset_left,
            402,
            408,
            puzzlename,
            greyinvert=False,
        )
        capture(
            target_offset_top - 122, target_offset_left, 402, 122, "word" + puzzlename
        )

    def extractword(self, puzzlename: str = "greyinvert_wordpuzzle.png") -> str:
        # Attempt to extract word from last saved recaptcha puzzle
        word = ocr(puzzlename, 0, 0, 300, 122)
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

    def verify(self, button: "Box") -> Tuple[int, int]:
        # Click verify
        left = int(button.left + 0.2 * button.width)
        top = int(button.top + 0.2 * button.height)
        right = int(button.left + 0.8 * button.width)
        bottom = int(button.top + 0.8 * button.height)
        return humanclick(left, top, right, bottom)

    def redundantclick(self, button: "Box") -> Tuple[int, int]:
        # Click arbitrary spot left of verify
        left = int(button.left - 1.2 * button.width)
        top = int(button.top - 0.1 * button.height)
        right = int(button.left - 0.2 * button.width)
        bottom = int(button.top + 1.0 * button.height)
        return humanclick(left, top, right, bottom)

    def extractartifacts(
        self, word: str, puzzlename: str = "puzzle.png"
    ) -> Dict[str, Tuple[int, int, int, int]]:
        """Find all artifacts that match word in last saved puzzle and save as images
        Return a dictionary of artifacts containing relative coordinates hashed by their filenames

        INPUT
        -----
        word : str

        puzzlename : str = "puzzle.png"
        """

        # Detect artifacts on-screen
        detections = objectdetection(word, puzzlename)  # type: List
        assert isinstance(detections, list)

        # Iterate through detections and return save img names and regions...
        result = dict()  # type: dict
        for thing in detections:

            try:
                # Crop images in puzzle contained within "box_points" & save to filename
                left = int(thing["box_points"][0])
                upper = int(thing["box_points"][1])
                right = int(thing["box_points"][2])
                lower = int(thing["box_points"][3])

                filename = "".join(["L", str(left), "T", str(upper), ".png"])

                img = Image.open(puzzlename)
                img_crop = img.crop((left, upper, right, lower))
                img_crop.save(filename)
                img_crop.close()
                img.close()
            except:
                pass
            else:
                result[filename] = thing["box_points"]

        return result

    def locateblacklist(
        self,
        cached_artifacts: Dict[str, Tuple[int, int, int, int]] = dict(),
        puzzlename: str = "puzzle.png",
    ) -> Set[Optional["Box"]]:
        """Locate any cached artifacts in puzzle and return a set of "Boxes" to be blacklisted.

        INPUT
        -----
        cached_artifacts : dict()
        puzzlename: str
        """

        # Check if cached artifacts is empty. If so, return empty set
        try:
            assert len(cached_artifacts) == 0
            return set()
        except:
            # Not empty, so iterate through and return their locations...
            result = set()  # type: set
            for cached_artifact in cached_artifacts:
                try:
                    img = locate(
                        "".join([getcwd(), "/", str(cached_artifact)]),
                        "".join([getcwd(), "/", str(puzzlename)]),
                        confidence=0.3,
                    )
                    assert hasattr(img, "left")
                except:
                    pass
                else:
                    # No exception thrown, so it's likely an area we want to blacklist
                    result.add(img)
                    # One result is enough
                    break
            return result

    def selectartifacts(
        self, button: "Box", artifacts: Dict[str, Tuple[int, int, int, int]]
    ) -> None:
        """Click on all artifacts, relative to button.

        INPUT
        -----
        cached_artifacts : dict()
        """

        puzzle_top = (
            int(button.top) - 428 + int((button.height + button.height % 2) / 2)
        )
        puzzle_left = (
            int(button.left) - 342 + int((button.width + button.width % 2) / 2)
        )

        try:
            for artifact in artifacts.values():
                left = artifact[0] + puzzle_left
                top = artifact[1] + puzzle_top
                right = artifact[2] + puzzle_left
                bottom = artifact[3] + puzzle_top

                clicked = humanclick(left, top, right, bottom)
                print(clicked, time.time())
        except:
            pass
