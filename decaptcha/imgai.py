from imageai.Detection import ObjectDetection
import os


class ImgAI(object):
    execution_path = os.getcwd()
    detector = ObjectDetection()

    def set_model(self, model_path: str) -> None:
        """Takes a filepath to a YOLOv3 model and loads model"""
        self.detector.setModelTypeAsYOLOv3()
        self.detector.setModelPath(model_path)
        self.detector.loadModel()

    def objectlib(self) -> set:
        custom = self.detector.CustomObjects()
        rv = set()
        for obj in custom.keys():
            for _ in obj.split(" "):
                rv.add(_)
        return rv

    def objectdetector(self, word: str, filename: str, minprobability=0.1) -> list:
        custom = self.detector.CustomObjects()
        for kw in custom.keys():
            for sub_key in kw.split(" "):
                if sub_key in word:
                    custom[kw] = True
        detections = self.detector.detectCustomObjectsFromImage(
            custom_objects=custom,
            input_image=os.path.join(self.execution_path, filename),
            output_image_path=os.path.join(self.execution_path, "labeled" + filename),
            minimum_percentage_probability=int(minprobability * 100),
        )
        return detections


if __name__ == "__main__":
    """
    CLI usage:
    $ python imgai.py bus puzzle.png yolo.h5
    """
    from sys import argv

    imgai = ImgAI()

    imgai.set_model(argv[3])
    detections = imgai.objectdetector(argv[1], argv[2])

    for eachObject in detections:
        print(
            eachObject["name"],
            " : ",
            eachObject["percentage_probability"],
            " : ",
            eachObject["box_points"],
        )
        print("--------------------------------")
