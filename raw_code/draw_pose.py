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
    ucorobot.draw_robots(frame, robot_POSE, robot_IDS, 0)
    '''
        Initialize the robot drawn process.
        
        Parameters
        ----------
        FRAME : OpenCV image
            OpenCV image.
        ROBOT_POSE : array
            Robot matrix of poses.
        ROBOT_IDS : array
            Robot matrix of IDS.
        MODE : int
            Style of drawn mode.
            0 --> Classic
            1 --> Dynamic
    '''
    #--- Show the frame
    cv2.imshow('frame', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break