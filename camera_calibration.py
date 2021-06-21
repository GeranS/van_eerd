import collections
import cv2
import pyrealsense2 as rs
import numpy as np
import json
import codecs
import sys
import time
import _thread

pipeline = rs.pipeline()
config = rs.config()

threshold_filter = rs.threshold_filter()
threshold_filter.set_option(rs.option.max_distance, 4)

config.enable_stream(rs.stream.depth, rs.format.z16, 30)
config.enable_stream(rs.stream.color, rs.format.bgr8, 30)

pipeline.start(config)
profile = pipeline.get_active_profile()

sensor = profile.get_device().first_depth_sensor()
sensor.set_option(rs.option.visual_preset, value=1)
sensor.set_option(rs.option.motion_range, value=200)

align_to = rs.stream.color
align = rs.align(align_to)

# Set colour palette to white to black
colorizer = rs.colorizer(3)

colorizer.set_option(rs.option.min_distance, 0)
colorizer.set_option(rs.option.max_distance, 0.1)
colorizer.set_option(rs.option.histogram_equalization_enabled, False)

loaded_object = json.loads(codecs.open('calib.json', 'r', encoding='utf-8').read())
mtx = np.asarray(loaded_object["mtx"])
dist = np.asarray(loaded_object["dist"])
newCameraMtx = np.asarray(loaded_object["newmtx"])
roi = loaded_object["roi"]

while 1:
    frames = pipeline.wait_for_frames()
    aligned_frames = align.process(frames)
    colour_frame = aligned_frames.get_color_frame()
    colour_frame = np.asanyarray(colour_frame.get_data())
    colour_frame = cv2.undistort(colour_frame, mtx, dist, None, newCameraMtx)

    cv2.imshow('calibrate', colour_frame)
    key = cv2.waitKey(1)

    if key == ord('s'):
        cv2.imwrite('calibratethisone.png', colour_frame)