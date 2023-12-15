import cv2
import ucorobot

#--- Get calibration parameters
mtx, dist, _, cam, API_cam, width, height, _ = ucorobot.read_calib()
robot_IDS, size_in = ucorobot.initialize()

#--- Video capture
cap = cv2.VideoCapture(cam, API_cam)

while True:

    ret, frame = cap.read()
    robot_POSE = ucorobot.get_pose(frame, 0, mtx, dist, robot_IDS, size_in)
    '''
        get_pose() --> Initialize the POSE calculation process.
        
        Parameters
        ----------
        GRAY : OpenCV image
            OpenCV image.
        MODE : int
            Pose parameters mode.
            0 --> Pixel based pose.
            1 --> Real ArUco based mode.
        MTX : array
            OpenCV camera matrix.
        DIST : array
            OpenCV distorsion matrix.
        ROBOT_IDS : array
            Robot matrix of IDS.
        SIZE_IN : int
            Initial number of units
    '''
    print(robot_POSE)