import cv2
import ucorobot

#-- Get calibration parameters
mtx, dist, _, cam, API_cam, width, height, _ = ucorobot.read_calib()
robot_IDS, size_in = ucorobot.initialize()

#-- UDP communication parameters
host = '192.168.43.10' 
port = 44444
robot_IP = ['192.168.43.231', '192.168.43.87']
UDP_mode = 'DIRECT'

#-- Initialize UDP communication
ucorobot.initialize_UDP(robot_IDS, host, port, robot_IP, UDP_mode)

#--- Video capture
cap = cv2.VideoCapture(cam, API_cam)

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

#-- Goal generation paramenters
initial_GOAL = [[500, 500, 30], [600, 300, 40]]
goal_file = 'sequence_multiple.csv'

#-- Initialize goals generation sequence
ucorobot.initialize_seq(initial_GOAL, goal_file)
'''
    Initialize goal generation sequence.
    
    Parameters
    ----------
    INIT_GOAL : array
        Sequence initial goals array.
    GOAL_FILE : str
        Sequence file name
'''

while True:

    ret, frame = cap.read()
    robot_POSE = ucorobot.get_pose(frame, 0, mtx, dist, robot_IDS, size_in)
    ucorobot.draw_robots(robot_POSE, robot_IDS, 1)
    robot_GOAL = ucorobot.goal_seq_time()
    '''
        goal_seq_time() --> Generate robot goals from sequence.
        
        No input parameters
        -------------------
    '''  
    ang_vel = ucorobot.trdiff_control_multiple(robot_POSE, robot_IDS, robot_GOAL, 'MIMC-VADOC', ctr_params)
    ucorobot.transmission_UDP(UDP_mode, ang_vel)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        ucorobot.UDP_close()
        break