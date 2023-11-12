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

#-- Pixel based goal position
robot_GOAL = [500, 500, 30]

#-- Parameters for controller
r = 3       # Radius of wheel
l = 10      # Distance between wheels
ks = 10     # Attraction force constant
d0 = 20     # Minimal attraction field distance
kw = 40     # Angular constant
U_max = 15  # Maximun robot velocity

ctr_params = [r, l, ks, d0, kw, U_max]

while True:

    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    robot_POSE = ucorobot.get_pose(gray, 0, mtx, dist, robot_IDS, size_in)
    ucorobot.draw_robots(frame, robot_POSE, robot_IDS, 0)

    print(robot_POSE)

    ang_vel = ucorobot.trdiff_control_single(frame, robot_POSE, robot_IDS, robot_GOAL, 'MIMC-VADOC', ctr_params)
    '''
        Initialize the single control process.
        Available for differential type robots.
        Only available for one single unit.
        
        Parameters
        ----------
        FRAME : OpenCV image
            OpenCV image.
        ROBOT_POSE : array
            Robot matrix of poses.
        ROBOT_IDS : array
            Robot matrix of IDS.
        ROBOT_GOAL : int
            Robot goal coordinates.
        CTR_MODE : str
            Differential robot controller type.
        CTR_PARAMS : array
            Parameters for the selected controller.
    '''
    
    #print(ang_vel)
    
    #--- Show the frame
    cv2.imshow('frame', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break