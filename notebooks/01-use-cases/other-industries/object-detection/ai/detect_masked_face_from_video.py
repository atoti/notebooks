"""
The class defined here is called to:
    - Detect masked/non-masked faces in videos
    - Store the predictions in a folder
    - Load the stored predictions into atoti and visualize
    - Add a new video, make and store detections and load them into atoti on the fly
"""


import numpy as np, pandas as pd
import time
import cv2
import os, sys
import datetime
import re
from datetime import timedelta

import torch, torchvision

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg

from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.structures import BoxMode


class MakePredictions:
    def __init__(self):
        """
        @param masked_face_detector: full path to the masked face detector model, including the model file
        @param conf_level: minimum probability to filter weak detections from the faceNet model
        @param video_from_camera: full path to the video recording associated to a specific camera
        @param output_folder: folder where the predictions are stored in csv files

        """
        self.masked_face_detector = None
        self.conf_level = None
        self.video_from_camera = None
        self.output_folder = None

    def ceil_dt(self, dt, delta):
        return dt + (datetime.datetime.min - dt) % delta

    def get_detections_from_camera(
        self, masked_face_detector, conf_level, video_from_camera, output_folder
    ):
        """
        @param masked_face_detector: full path to the masked face detector model weights, including the model file ("final_model.path")
        @param conf_level: minimum probability to filter weak detections from the faceNet model
        @param video_from_camera: full path to the video recording associated to a specific camera
        @param output_folder: folder where the predictions are stored in csv files
        """

        self.masked_face_detector = masked_face_detector
        self.conf_level = conf_level
        self.video_from_camera = video_from_camera
        self.output_folder = output_folder

        # load our serialized face detector model from disk
        print("Loading the detector model...\n")

        cfg = get_cfg()
        cfg.merge_from_file(
            model_zoo.get_config_file(
                "COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml"
            )
        )
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = (
            self.conf_level
        )  # 0.5 set threshold for this model
        cfg.MODEL.WEIGHTS = self.masked_face_detector
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2
        predictor = DefaultPredictor(cfg)

        # Time here is in seconds, so we do the increament  in seconds
        time_increment = 5

        # here is the directory to the video that we are playing
        vs = cv2.VideoCapture(self.video_from_camera)
        prev_time = time.time()

        labels = []
        probabilities = []
        time_stamp = []
        quarter_time_stamp = []
        video_id = []

        # Naming the output file, which can be also used as a video id
        print(self.video_from_camera)
        output_csv = self.video_from_camera.split(os.sep)[-1]
        current_video_id = re.split("_", output_csv)[-1].split(".")[0]
        #         current_video_id = ''.join(output_csv.split('.')[:-1])

        print("Reading the video...\n")
        ret, frame = vs.read()

        # loop over the frames from the video stream
        while vs.isOpened():
            # grab the frame from the threaded video stream and resize it to have a maximum width of 400 pixels
            ret, frame = vs.read()

            if ret == True:
                # frame = imutils.resize(frame, width=400)
                frame = cv2.resize(frame, (3000, 2000))

                # detect faces in the frame and determine if they are wearing a face mask or not
                # (locs, preds) = predict_helper.detect_and_predict_mask(frame, faceNet, maskNet, conf_level)
                outputs = predictor(frame)
                current_labels = outputs["instances"].to("cpu").pred_classes.tolist()
                current_probabilities = outputs["instances"].to("cpu").scores.tolist()
                now = datetime.datetime.now()
                current_time_stamp = now.strftime("%Y-%m-%d %H:%M:%S:%f")
                current_quarter_time_stamp = now.strftime("%Y-%m-%d %H:%M:%S")

                #                 # uncomment below code to see the prediction box
                #                 #################################
                #                 v = Visualizer(frame[:, :, ::-1],
                #                 metadata=masked_face_metadata,
                #                 scale=1.0, #0.8
                #                 instance_mode=ColorMode.IMAGE
                #                 )
                #                 out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
                #                 cv2.imshow('frame', out.get_image()[:, :, ::-1])

                # if locs == []:
                if not labels:
                    probabilities.append("")
                    labels.append("")
                    time_stamp.append(current_time_stamp)
                    video_id.append(current_video_id)
                    qtr_ts = self.ceil_dt(now, timedelta(seconds=time_increment))
                    quarter_time_stamp.append(qtr_ts.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    labels += [["No Mask", "Mask"][y_hat] for y_hat in current_labels]
                    probabilities += [p * 100 for p in current_probabilities]
                    time_stamp += [current_time_stamp] * len(current_labels)
                    video_id += [current_video_id] * len(current_labels)
                    qtr_ts = self.ceil_dt(now, timedelta(seconds=time_increment))
                    quarter_time_stamp += [qtr_ts.strftime("%Y-%m-%d %H:%M:%S")] * len(
                        current_labels
                    )

                current_time = time.time()

                if current_time - prev_time >= time_increment:
                    # appending the probabilities into a dataframe
                    prediction_df = pd.DataFrame(
                        {
                            "predictions": probabilities,
                            "label": labels,
                            "timestamp": time_stamp,
                            "quarter_timestamp": quarter_time_stamp,
                            "video_id": video_id,
                        }
                    )

                    prediction_df["face_id"] = prediction_df.groupby(
                        "timestamp"
                    ).cumcount()
                    prediction_df = prediction_df[
                        [
                            "face_id",
                            "predictions",
                            "label",
                            "timestamp",
                            "quarter_timestamp",
                            "video_id",
                        ]
                    ]

                    # renaming the output csv file to make it in the csv format
                    #                     print(os.path.join(output_folder, output_csv))
                    output_csv = "".join(output_csv.split(".")[:-1]) + ".csv"
                    with open(os.path.join(output_folder, output_csv), "a") as f:
                        prediction_df.to_csv(
                            f, header=f.tell() == 0, index=False, line_terminator="\n"
                        )

                    prev_time = time.time()
                    labels = []
                    probabilities = []
                    time_stamp = []
                    quarter_time_stamp = []
                    video_id = []

            else:
                break

            # if the `q` key was pressed, break from the loop
            if cv2.waitKey(1) == ord("q"):
                break

        # do a bit of cleanup
        vs.release()
        cv2.destroyAllWindows()
