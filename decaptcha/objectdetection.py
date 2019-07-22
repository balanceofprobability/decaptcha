import matplotlib

matplotlib.use("agg")
from imageai.Detection import ObjectDetection
import os


def objectdetection(target: str = "target.png") -> list:
    execution_path = os.getcwd()

    detector = ObjectDetection()
    detector.setModelTypeAsYOLOv3()
    detector.setModelPath(os.path.join(execution_path, "yolo.h5"))
    detector.loadModel()
    detections = detector.detectObjectsFromImage(
        input_image=os.path.join(execution_path, target),
        output_image_path=os.path.join(execution_path, "labeled" + target),
        minimum_percentage_probability=30,
    )
    return detections


if __name__ == "__main__":
    detections = objectdetection()
    for eachObject in detections:
        print(
            eachObject["name"],
            " : ",
            eachObject["percentage_probability"],
            " : ",
            eachObject["box_points"],
        )
        print("--------------------------------")
