import math

L1, L2, L3 = 612.9, 571.6, 115.7
D1, D2, D34 = 176, 127.8, 115.7

BASE_ANGLE_OFFSET = - 0.5 * math.pi
SHOULDER_ANGLE_OFFSET = 0
ELBOW_ANGLE_OFFSET = 0 #math.pi
WRIST1_ANGLE_OFFSET = 0

EOAT_WRIST2_OFFSET = 120


# Returns base angle and wrist 2 angle
def coordinates_to_joints(x, y, z, facing='s'):

    x = -x
    z = -z

    angle0 = math.atan(x / y) - math.asin((D1 - D2 + D34) / math.sqrt((x ** 2) + (y ** 2)))
    angle2 = math.acos(((x ** 2) + (y ** 2) + ((z + L3) ** 2) - (L1 ** 2) - (L2 ** 2))/(2*L1*L2))
    angle1 = math.atan((z + L3) / math.sqrt(x ** 2 + y ** 2)) - math.atan(
        (L2 * math.sin(angle2)) / (L1 + L2 * math.cos(angle2)))
    angle3 = (-angle1 - angle2)

    base_angle = angle0 + BASE_ANGLE_OFFSET
    shoulder_angle = angle1 + SHOULDER_ANGLE_OFFSET
    elbow_angle = angle2 + ELBOW_ANGLE_OFFSET
    wrist1_angle = angle3 + WRIST1_ANGLE_OFFSET

    print('base angle: ' + str(base_angle * 57.295))
    print('shoulder angle: ' + str(shoulder_angle * 57.295))
    print('elbow angle: ' + str(elbow_angle * 57.295))
    print('wrist 1 angle: ' + str(wrist1_angle * 57.295))


coordinates_to_joints(-200, 500, 102.8)
