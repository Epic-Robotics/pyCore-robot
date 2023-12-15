import cv2
import ucorobot

#--- Get calibration parameters
mtx, dist, _, cam, API_cam, width, height, _ = ucorobot.read_calib()
robot_IDS, size_in = ucorobot.initialize()

#--- Video capture
cap = cv2.VideoCapture(cam, API_cam)

#-- Pixel based goal position (Based on robot's number)
robot_GOAL = [[500, 500, 30],
              [600, 600, 40],
              [500, 500, 30],
              [600, 600, 40],
              [500, 500, 30]]

#-- Parameters for controller
r = 3               # Radius of wheel (pixels)
l = 10              # Distance between wheels (pixels)
ks = 10             # Attraction force constant
d0 = 20             # Minimal attraction field distance
kw = 40             # Angular constant
U_max = 15          # Maximun robot velocity
kr = 500000000      # Repulsion force constant
L0 = 50             # Minimal repulsion field distance

ctr_params = [r, l, ks, d0, kw, U_max, kr, L0]

while True:

    ret, frame = cap.read()
    robot_POSE = ucorobot.get_pose(frame, 0, mtx, dist, robot_IDS, size_in)
    ucorobot.draw_robots(robot_POSE, robot_IDS, 1)

    ang_vel = ucorobot.trdiff_control_multiple(robot_POSE, robot_IDS, robot_GOAL, 'MIMC-VADOC', ctr_params)
    '''
        trdiff_control_multiple() --> Initialize the multiple control process.
        Available for differential type robots.
        Only available for multiple units.
        
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