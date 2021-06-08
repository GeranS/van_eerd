import cv2
import pyrealsense2 as rs
import numpy as np
import json
import codecs
import sys

from box_detector import BoxDetector


class Main():
    def __init__(self):
        self.pipeline = rs.pipeline()
        config = rs.config()

        self.threshold_filter = rs.threshold_filter()
        self.threshold_filter.set_option(rs.option.max_distance, 4)

        config.enable_stream(rs.stream.depth, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, rs.format.bgr8, 30)

        self.pipeline.start(config)
        self.profile = self.pipeline.get_active_profile()

        align_to = rs.stream.color
        self.align = rs.align(align_to)

        self.box_detector = BoxDetector()

        self.main_loop()

    def main_loop(self):
        while 1:
            frames = self.pipeline.wait_for_frames()
            aligned_frames = self.align.process(frames)
            colour_frame = aligned_frames.get_color_frame()
            colour_frame = np.asanyarray(colour_frame.get_data())

            detections, im0 = self.box_detector.detect_boxes(colour_frame.copy())

            cv2.imshow('box', im0)
            cv2.imshow('no detection', colour_frame)
            key = cv2.waitKey(1)

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
