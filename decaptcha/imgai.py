import matplotlib

matplotlib.use("agg")
from imageai.Detection import ObjectDetection
import os

execution_path = os.getcwd()
detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath(os.path.join(execution_path, "yolo.h5"))
detector.loadModel()


def objectlib() -> set:
    custom = detector.CustomObjects()
    rv = set()
    for obj in custom.keys():
        for _ in obj.split(" "):
            rv.add(_)
    return rv


def objectdetector(word: str, filename: str, minprobability=0.1) -> list:
    custom = detector.CustomObjects()
    for kw in custom.keys():
        for sub_key in kw.split(" "):
            if sub_key in word:
                custom[kw] = True
    detections = detector.detectCustomObjectsFromImage(
        custom_objects=custom,
        input_image=os.path.join(execution_path, filename),
        output_image_path=os.path.join(execution_path, "labeled" + filename),
        minimum_percentage_probability=int(minprobability * 100),
    )
    return detections


if __name__ == "__main__":
    """
    cmd usage:
    $ python imgai.py bus puzzle.png
    """
    from sys import argv

    detections = objectdetector(argv[1], argv[2])
    for eachObject in detections:
        print(
            eachObject["name"],
            " : ",
            eachObject["percentage_probability"],
            " : ",
            eachObject["box_points"],
        )
        print("--------------------------------")
