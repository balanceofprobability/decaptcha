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


def objectdetection(word: str, target: str = "target.png") -> list:
    custom = detector.CustomObjects()
    for kw in custom.keys():
        if kw in word:
            custom[kw] = True
            break
    detections = detector.detectCustomObjectsFromImage(
        custom_objects=custom,
        input_image=os.path.join(execution_path, target),
        output_image_path=os.path.join(execution_path, "labeled" + target),
        minimum_percentage_probability=30,
    )
    return detections


if __name__ == "__main__":
    from sys import argv

    detections = objectdetection(argv[1])
    for eachObject in detections:
        print(
            eachObject["name"],
            " : ",
            eachObject["percentage_probability"],
            " : ",
            eachObject["box_points"],
        )
        print("--------------------------------")
