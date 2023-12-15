import cv2
from pycore_robot import ucoRobot

#--- Get calibration parameters
mtx, dist, _, cam, API_cam, width, height, _ = ucoRobot.read_calib()
robot_IDS, size_in = ucoRobot.initialize()

#--- Video capture
cap = cv2.VideoCapture(cam, API_cam)

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
    robot_POSE = ucoRobot.get_pose(frame, 0, mtx, dist, robot_IDS, size_in)
    ucoRobot.draw_robots(robot_POSE, robot_IDS, 1)

    print(robot_POSE)

    ang_vel = ucoRobot.trdiff_control_single(robot_POSE, robot_IDS, robot_GOAL, 'MIMC-VADOC', ctr_params)
    '''
        trdiff_control_single() --> Initialize the single control process.
        Available for differential type robots.
        Only available for one single unit.
        
        Parameters
        ----------
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
    
    print(ang_vel)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break