import numpy as np
import torch

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import non_max_suppression, scale_coords, xyxy2xywh
from utils.plots import plot_one_box
from utils.torch_utils import select_device


class DetectedBox():
    def __init__(self, x, y, w, h, conf, grabbed=False):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.z = 0
        self.r = 0
        self.conf = conf
        self.grabbed = grabbed


class BoxDetector():
    def __init__(self):
        self.device = select_device('')
        self.half = self.device.type != 'cpu'
        self.weights_url = './weights/final dataset.pt'
        self.model = attempt_load(self.weights_url, map_location=self.device)
        self.stride = int(self.model.stride.max())
        self.image_size = 640
        self.confidence_threshold = 0.8
        self.iou_threshold = 0.45

        if self.half:
            self.model.half()

    def detect_boxes(self, im0):
        image = letterbox(im0, self.image_size, stride=self.stride)[0]
        image = image[:, :, ::-1].transpose(2, 0, 1)
        image = np.ascontiguousarray(image)
        image = torch.from_numpy(image).to(self.device)
        image = image.half() if self.half else image.float()
        image /= 255.0

        if image.ndimension() == 3:
            image = image.unsqueeze(0)

        prediction = self.model(image, augment='store_true')[0]
        prediction = non_max_suppression(prediction, self.confidence_threshold, self.iou_threshold,
                                         agnostic='store_true')

        detections = []

        #x_scale_factor = image.shape[0] / im0.shape[0]
        #y_scale_factor = image.shape[1] / im0.shape[1]

        for i, det in enumerate(prediction):
            gn = torch.tensor(image.shape)[[1, 0, 1, 0]]

            if len(det):
                det[:, :4] = scale_coords(image.shape[2:], det[:, :4], im0.shape).round()

                for *xyxy, conf, cls in reversed(det):
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()
                    unscaled_x, unscaled_y, unscaled_w, unscaled_h = xywh[0], xywh[1], xywh[2], xywh[3]

                    #x, y = unscaled_x / x_scale_factor, unscaled_y / y_scale_factor
                    #w, h = unscaled_w / x_scale_factor, unscaled_h / y_scale_factor
                    x, y = xyxy[0], xyxy[1]
                    w = xyxy[2] - xyxy[0]
                    h = xyxy[3] - xyxy[1]

                    detections.append(DetectedBox(int(x), int(y), int(w), int(h), conf))
                    plot_one_box(xyxy, im0, label="Box " + str(conf))

        return detections, im0

    def detections_to_grid(self, detections):
        columns = []

        sorted_by_x = sorted(detections, key=lambda det: det.x, reverse=True)

        while len(sorted_by_x) != 0:
            current_column = []
            current_column_x = sorted_by_x[0].x

            while True:
                if len(sorted_by_x) > 0 and current_column_x - 30 < sorted_by_x[0].x < current_column_x + 30:
                    current_column.append(sorted_by_x[0])
                    sorted_by_x.remove(sorted_by_x[0])
                    print("sorted_by_x length: " + str(len(sorted_by_x)))
                    continue
                break

            current_column = sorted(current_column, key=lambda det: det.y, reverse=True)

            columns.append(current_column)

        return columns
