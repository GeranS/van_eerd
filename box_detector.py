import numpy as np
import torch

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import non_max_suppression, scale_coords, xyxy2xywh
from utils.plots import plot_one_box
from utils.torch_utils import select_device


class BoxDetector():
    def __init__(self):
        self.device = select_device('')
        self.half = self.device.type != 'cpu'
        self.weights_url = './weights/last.pt'
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

        for i, det in enumerate(prediction):
            gn = torch.tensor(image.shape)[[1, 0, 1, 0]]

            if len(det):
                det[:, :4] = scale_coords(image.shape[2:], det[:, :4], im0.shape).round()

                for *xyxy, conf, cls in reversed(det):
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1,4)) / gn).view(-1).tolist()
                    detections.append((xywh, conf))
                    plot_one_box(xyxy, im0, label="Box " + str(conf))

        return detections, im0