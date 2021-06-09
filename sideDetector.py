import cv2
import numpy as np


class SideDetector:

    def slice_side(self, img, side, percentage=0.2):
        colums, rows = np.shape(img)
        if side == 'n' or side == 's':
            if side == 's':
                img = np.flip(img, 0)
            sliced = img[:int(percentage * colums), :]
        elif side == 'e' or side == 'w':
            if side == 'w':
                img = np.flip(img, 1)
            sliced = img[:, :int(percentage * rows)]

        return sliced

    def image_to_bw(self, img, thresh=127):
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        ret, img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)
        img = img.astype(np.uint8)
        return img

    def black_pixels(self, img, side):
        total_b = 0
        sliced = self.slice_side(img, side)
        unique = np.unique(sliced, return_counts=True)
        for i in range(len(unique[0])):
            if unique[0][i] < 127:
                total_b += unique[1][i]
                # print(total_b)
                colums, rows = np.shape(sliced)
        return (total_b / (rows * colums))  # percentage factor of values under 127

    def which_side(self, img, side1, side2, percentage=0.2):
        if self.black_pixels(img, side1) == self.black_pixels(img, side2):
            return 'equal'
        elif self.black_pixels(img, side1) > self.black_pixels(img, side2):
            return side2
        else:
            return side1

    def zoom(self, img, lt_corner, rb_corner):
        return img[lt_corner[1]:rb_corner[1], lt_corner[0]:rb_corner[0]]

    def detect_side(self, img, lt_corner, rb_corner, side1='n', side2='e'):
        img = self.zoom(img, lt_corner, rb_corner)
        img = self.image_to_bw(img)
        side = self.which_side(img, side1, side2)
        return side
