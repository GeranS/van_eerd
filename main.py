import collections
import cv2
import pyrealsense2 as rs
import numpy as np
import json
import codecs
import sys
import datetime

from box_detector import BoxDetector
from sideDetector import SideDetector


class Main:
    def __init__(self):
        self.pipeline = rs.pipeline()
        config = rs.config()

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

        self.main_loop()

    def main_loop(self):
        while 1:
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

            counter = 1

            for column in grid:
                for det in column:
                    center_x = det.x + int(det.w / 2)
                    center_y = det.y + int(det.h / 2)
                    cv2.putText(im0, str(counter), (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (255, 120, 5), 2)
                    counter += 1

            top_right_det = grid[0][len(grid[0]) - 1]

            x, y, w, h = top_right_det.x, top_right_det.y, top_right_det.w, top_right_det.h

            lt = (x, y)
            rb = (x + w, y + h)

            # try:
            side = self.side_detector.detect_side(depth_colormap, lt, rb)
            cv2.putText(im0, "side: " + side, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 120, 5), 2)
            # except:
            #    cv2.putText(im0, "Could not find side", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 120, 5), 2)

            cv2.imshow('box', cv2.resize(im0, (1600, 900)))

            cv2.rectangle(depth_colormap, (x, y), (x + w, y + h), (255, 0, 255), 2)
            cv2.imshow('depth', cv2.resize(depth_colormap, (1600, 900)))
            key = cv2.waitKey(1)

            if key == ord('s'):
                cv2.imwrite('./saved_images/detection' + str(datetime.datetime.now()) + '.png', im0)

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


Main()
