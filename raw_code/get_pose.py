import cv2
import ucorobot

#--- Get calibration parameters
mtx, dist, _, cam, API_cam, width, height, _ = ucorobot.read_calib()
robot_IDS, size_in = ucorobot.initialize()

#--- Video capture
cap = cv2.VideoCapture(cam, API_cam)

#-- Resolution set
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

while True:

    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    robot_POSE = ucorobot.get_pose(gray, 0, mtx, dist, robot_IDS, size_in)
    '''
        Initialize the POSE calculation process.
        
        Parameters
        ----------
        GRAY : OpenCV image
            OpenCV gray image.
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


    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break