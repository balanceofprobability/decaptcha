import matplotlib

matplotlib.use("agg")
from imageai.Detection import ObjectDetection
import os

execution_path = os.getcwd()
detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath(os.path.join(execution_path, "yolo.h5"))
detector.loadModel()


def objectlib() -> list:
    custom = detector.CustomObjects()
    return list(custom.keys())


def objectdetection(word: str, filename: str) -> list:
    custom = detector.CustomObjects()
    for kw in custom.keys():
        if kw in word:
            custom[kw] = True
    detections = detector.detectCustomObjectsFromImage(
        custom_objects=custom,
        input_image=os.path.join(execution_path, filename),
        output_image_path=os.path.join(execution_path, "labeled" + filename),
        minimum_percentage_probability=10,
    )
    return detections


if __name__ == "__main__":
    """
    cmd usage:
    $ python objectdetection bus puzzle.png
    """
    from sys import argv

    detections = objectdetection(argv[1], argv[2])
    for eachObject in detections:
        print(
            eachObject["name"],
            " : ",
            eachObject["percentage_probability"],
            " : ",
            eachObject["box_points"],
        )
        print("--------------------------------")
