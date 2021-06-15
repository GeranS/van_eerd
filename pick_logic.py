import collections
import cv2
import pyrealsense2 as rs
import numpy as np
import json
import codecs
import sys
import datetime

from box_detector import BoxDetector
from communication.ur_service import URService, URCommand
from sideDetector import SideDetector


class PickLogic:
    def __init__(self, main):
        self.pipeline = rs.pipeline()
        config = rs.config()

        self.main = main

        self.current_frame = None

        self.threshold_filter = rs.threshold_filter()
        self.threshold_filter.set_option(rs.option.max_distance, 4)

        config.enable_stream(rs.stream.depth, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, rs.format.bgr8, 30)

        self.pipeline.start(config)
        self.profile = self.pipeline.get_active_profile()

        self.sensor = self.profile.get_device().first_depth_sensor()
        self.sensor.set_option(rs.option.visual_preset, value=1)
        self.sensor.set_option(rs.option.motion_range, value=200)

        align_to = rs.stream.color
        self.align = rs.align(align_to)

        # Set colour palette to white to black
        self.colorizer = rs.colorizer(3)

        self.colorizer.set_option(rs.option.min_distance, 0)
        self.colorizer.set_option(rs.option.max_distance, 0.1)
        self.colorizer.set_option(rs.option.histogram_equalization_enabled, False)

        self.box_detector = BoxDetector()
        self.side_detector = SideDetector()
        self.ur_service = URService()

        self.pile_grid = None
        self.busy = False

        self.main_loop()

    def get_pile_grid(self):
        frames = self.pipeline.wait_for_frames()

        aligned_frames = self.align.process(frames)
        colour_frame = aligned_frames.get_color_frame()
        colour_frame = np.asanyarray(colour_frame.get_data())

        threshold_z = self.determine_top_layer_distance()

        self.threshold_filter.set_option(rs.option.max_distance, threshold_z + 0.05)
        depth_frame = aligned_frames.get_depth_frame()
        depth_frame = self.threshold_filter.process(depth_frame)
        depth_colormap = np.asanyarray(self.colorizer.colorize(depth_frame).get_data())

        detections, im0 = self.box_detector.detect_boxes(colour_frame.copy())

        grid = self.box_detector.detections_to_grid(detections)

        distance = self.determine_top_layer_distance()

        col = 0
        while col < len(self.pile_grid):
            row = 0
            while row < self.pile_grid[col]:
                self.pile_grid[col][row].z = distance

        return grid

    def main_loop(self):
        while 1:
            if self.main.state == 0 or self.busy:
                continue

            if self.pile_grid is None:
                self.pile_grid = self.get_pile_grid()
                continue

            if len(self.pile_grid) == 0:
                self.ur_service.send_command_to_ur(URCommand.grab_sheet)
                self.busy = True
                continue

            col = 0
            while col < len(self.pile_grid):
                row = 0
                while row < self.pile_grid[col]:
                    if self.pile_grid[col][row].grabbed is False:
                        self.ur_service.send_command_to_ur(URCommand.grab_stack, self.pile_grid[col][row])
                        self.pile_grid[col][row].grabbed = True
                        self.busy = True
                        continue

    def determine_top_layer_distance(self):
        frames = self.pipeline.wait_for_frames()

        # Set distance to 4 meters so it can see the whole pallet
        self.threshold_filter.set_option(rs.option.max_distance, 4)

        depth_frame = frames.get_depth_frame()
        depth_frame = self.threshold_filter.process(depth_frame)

        depth_image = np.asanyarray(depth_frame.get_data())
        depth_image = depth_image[120:360, 120:520]
        depth_image = depth_image[depth_image != 0]

        counter = collections.Counter(depth_image)
        most_common = counter.most_common(500)

        smallest_most_common = 10000000

        for m in most_common:
            if m[0] < smallest_most_common:
                smallest_most_common = m[0]

        closest_object_in_meters = float(smallest_most_common) * self.sensor.get_option(rs.option.depth_units)
        return closest_object_in_meters

    def generate_distortion_matrix(self):
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        objp = np.zeros((15 * 8, 3), np.float32)
        objp[:, :2] = np.mgrid[0:15, 0:8].T.reshape(-1, 2)
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.

        while 1:
            frames = self.pipeline.wait_for_frames()
            aligned_frames = self.align.process(frames)
            colour_frame = aligned_frames.get_color_frame()
            colour_frame = np.asanyarray(colour_frame.get_data())

            gray = cv2.cvtColor(colour_frame, cv2.COLOR_BGR2GRAY)

            cv2.imshow("calibration", colour_frame)

            key = cv2.waitKey(1)

            if key == ord('d'):
                # Find the chess board corners
                ret, corners = cv2.findChessboardCorners(gray, (15, 8), None)
                # If found, add object points, image points (after refining them)
                if ret:
                    objpoints.append(objp)
                    corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    imgpoints.append(corners)
                    print('Data point added.')
                # Save and exit calibration
            elif key == ord('m'):
                ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
                h, w = colour_frame.shape[:2]
                newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

                data_to_save = {
                    "mtx": mtx.tolist(),
                    "dist": dist.tolist(),
                    "newmtx": newcameramtx.tolist(),
                    "roi": roi
                }

                json.dump(data_to_save, codecs.open('calib.json', 'w', encoding='utf-8'))
                break
                # Exit calibration
            elif key == 27:
                sys.exit()

