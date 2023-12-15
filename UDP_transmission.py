import cv2
import ucorobot

#-- Get calibration parameters
mtx, dist, _, cam, API_cam, width, height, _ = ucorobot.read_calib()
robot_IDS, size_in = ucorobot.initialize()

#-- UDP communication parameters
host = '192.168.43.10' 
port = 44444
robot_IP = ['192.168.43.19',
            '192.168.43.215']
UDP_mode = 'DIRECT'

#-- Initialize UDP communication
ucorobot.initialize_UDP(robot_IDS, host, port, robot_IP, UDP_mode)
'''
    Initialize UDP communication protocol.
    Wi-Fi based communication.
    Multiple communication modes.
    
    Parameters
    ----------
    ROBOT_IDS : array
        Robot matrix of IDS.
    HOST : str
        Wi-Fi connection host IP.
    PORT : int
        Wi-Fi connection port.
    ROBOT_IP : array
        List of robots/PC's IP's.
    UDP_MODE : str
        Connection Mode.
        'DIRECT' = PC to Robot direct connection
        'MASTER' = PC to PC master connection
        'LISTENER' = PC to PC listener connection
'''
#--- Video capture
cap = cv2.VideoCapture(cam, API_cam)

#-- Pixel based goal position
robot_GOAL = [[500, 500, 30],
              [600, 600, 40]]

#-- Parameters for controller
r = 3               # Radius of wheel
l = 10              # Distance between wheels
ks = 10             # Attraction force constant
d0 = 20             # Minimal attraction field distance
kw = 40             # Angular constant
U_max = 70          # Maximun robot velocity
kr = 500000000      # Repulsion force constant
L0 = 50             # Minimal repulsion field distance

ctr_params = [r, l, ks, d0, kw, U_max, kr, L0]

while True:

    ret, frame = cap.read()
    robot_POSE = ucorobot.get_pose(frame, 0, mtx, dist, robot_IDS, size_in)
    ucorobot.draw_robots(robot_POSE, robot_IDS, 1)
    ang_vel = ucorobot.trdiff_control_multiple(robot_POSE, robot_IDS, robot_GOAL, 'MIMC-VADOC', ctr_params)

    ucorobot.transmission_UDP(UDP_mode, ang_vel)
    '''
        transmission_UDP() --> Data transmission.
        
        Parameters
        ----------
        UDP_MODE : STR
            Connection Mode.
            'DIRECT' = PC to Robot direct connection
            'MASTER' = PC to PC master connection
            'LISTENER' = PC to PC listener connection
        TR_DATA : STR
            Pose or angular velocities data for transmission.
    '''

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        ucorobot.UDP_close()
        break