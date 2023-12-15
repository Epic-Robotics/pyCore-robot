import cv2
from pycore_robot import ucoRobot

#--- Get calibration parameters
mtx, dist, _, cam, API_cam, width, height, _ = ucoRobot.read_calib()
robot_IDS, size_in = ucoRobot.initialize()

#--- Video capture
cap = cv2.VideoCapture(cam, API_cam)

while True:

    ret, frame = cap.read()
    robot_POSE = ucoRobot.get_pose(frame, 0, mtx, dist, robot_IDS, size_in)
    ucoRobot.draw_robots(robot_POSE, robot_IDS, 0)
    '''
        draw_robots() --> Initialize the robot drawn process.
        
        Parameters
        ----------
        ROBOT_POSE : array
            Robot matrix of poses.
        ROBOT_IDS : array
            Robot matrix of IDS.
        MODE : int
            Style of drawn mode.
            0 --> Classic
            1 --> Dynamic
    '''

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break