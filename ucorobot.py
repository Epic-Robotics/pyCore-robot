import numpy as np
import cv2
import glob
import argparse
import os
import time
import cv2.aruco as aruco
import math
import sys
import socket
import csv

Uco = argparse.ArgumentParser("Uco Robots library parameters")
subparsers = Uco.add_subparsers(help='Command help for Uco Robots library')

calib = subparsers.add_parser('calib', help='Calibration method')
calib.add_argument("-m", "--mode", type=int, help="Calibration mode. 0 --> Get new calibration images. 1 --> Use existing files", default=0, required=False)
calib.add_argument("-ms", "--marker_size", type=float, help="Length of one edge (in meters)", default=0.1)
calib.add_argument("-d", "--dct", type=str, help="Predefined markers dictionaries/sets (default=aruco.DICT_ARUCO_ORIGINAL)", default="aruco.DICT_ARUCO_ORIGINAL")
calib.add_argument("-bw", "--board_width", type=int, help="Width of checkerboard (default=9)",  default=9)
calib.add_argument("-bh", "--board_height", type=int, help="Height of checkerboard (default=6)", default=6)
calib.add_argument("-c", "--cam", type=int, help="Camera source (default=0)", default=0)
calib.add_argument("-ac", "--API_cam", type=str, help="Camera capture API (default=None)", default=None)
calib.add_argument("-wi", "--width", type=int, help="Width of camera resolution (default=640)", default=640)
calib.add_argument("-he", "--height", type=int, help="Height of camera resolution (default=480)", default=480)

pose = subparsers.add_parser('pose', help = 'Get positional parameters')
pose.add_argument("-g", "--gray", help="OpenCV gray image.", required=False)
pose.add_argument("-m", "--mode", type=int, help="Pose parameters mode. 0 --> Pixel based pose. 1 --> Real ArUco based mode.", default=0, required=False)
pose.add_argument("-mt", "--mtx", help="OpenCV camera matrix.", required=False)
pose.add_argument("-di", "--dist", help="OpenCV distorsion matrix.", required=False)
pose.add_argument("-r", "--robot_IDS", help="Robot matrix of IDS.", required=False)
pose.add_argument("-s", "--size_in", type=int, help="Initial number of units")

draw = subparsers.add_parser('draw', help = 'Draw real-time robots')
draw.add_argument("-f", "--frame", help="Camera image frame.")
draw.add_argument("-rb", "--robot_POSE", help="Robot matrix of POSES.")
draw.add_argument("-r", "--robot_IDS", help="Robot matrix of IDS.")
draw.add_argument("-m", "--mode", type=int, help="Style of draw mode", default=0)

ctrdiff = subparsers.add_parser('ctrdiff', help = "PyCore_Robot default differential robot controllers")
ctrdiff.add_argument("-f", "--frame", help="Camera image frame.")
ctrdiff.add_argument("-rb", "--robot_POSE", help="Robot matrix of POSE.")
ctrdiff.add_argument("-ri", "--robot_IDS", help="Robot ID")
ctrdiff.add_argument("-rg", "--robot_GOAL", help="Robot goal coordinates.")
ctrdiff.add_argument("-cm", "--ctr_mode", type=str, help="Differential robot controller type", default="MIMC-VADOC")
ctrdiff.add_argument("-p", "--ctr_params", help="Parameters for the selected controller")

UDP_com = subparsers.add_parser('UDP_com', help = "Initialize UDP communication parameters")
UDP_com.add_argument("-ri", "--robot_IDS", help="Robot matrix of IDS")
UDP_com.add_argument("-ho", "--host", type=str, help="Wi-Fi connection host IP")
UDP_com.add_argument("-po", "--port", type=int, help="Wi-Fi connection port")
UDP_com.add_argument("-ip", "--robot_PC_IP", help="List of robots/PC's IP's")
UDP_com.add_argument("-m", "--mode", type=str, help="Connection Mode")

UDP_transmission = subparsers.add_parser('UDP_transmission', help = "Transmit and receive data")
UDP_transmission.add_argument("-m", "--mode", type=str, help="Connection Mode")
UDP_transmission.add_argument("-da", "--tr_data", help="Pose or angular velocities data for transmission")

seq_init = subparsers.add_parser('Goal sequence', help = "Goal sequence generation")
seq_init.add_argument("-si", "--init_goal", help="Initial goal position")
seq_init.add_argument("-fi", "--goal_file", type=str, help="Goal position file in csv")

Uco_args = Uco.parse_args()
pose_args = pose.parse_args()
calib_args = calib.parse_args()
draw_args = draw.parse_args()
ctrdiff_args = ctrdiff.parse_args()
UDP_com_args = UDP_com.parse_args()
UDP_transmission_args = UDP_transmission.parse_args()
seq_init_args = seq_init.parse_args()

def get_images(cam, API_cam, board_width, board_height, width, height):
    
    WAIT_TIME = 50
    cap = cv2.VideoCapture(cam, API_cam)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    font = cv2.FONT_HERSHEY_PLAIN
    
    print("----- CALIBRATION IMAGE TAKING -----")
    print(" ")
    print("- Please use a cheesboard with "+str(board_width)+" width inner corners")
    print("- Please use a cheesboard with "+str(board_height)+" height inner corners")
    print("- Please change position and orientation of the chessboard")
    print(" ")
    
    time.sleep(5)
    
    image_number = input("Please enter the number of images to calibrate:\n")
    
    for i in range(int(image_number)):
        _, frame = cap.read()
        d = os.path.dirname(__file__)
        p = r'{}/Calibration_Images'.format(d)
        cv2.imwrite(os.path.join(p , 'img_{}.jpg'.format(i)), frame)
        cv2.putText(frame, (str(i)),
                   (int(width/2), int(height/2)),
                   font, 4, (0,255,255), 2, cv2.LINE_AA)
        cv2.imshow('Captured Image', frame)
        cv2.waitKey(WAIT_TIME)
    cv2.destroyAllWindows()
    
def calibration(mode = calib_args.mode, 
                marker_size = calib_args.marker_size, 
                dct = calib_args.dct, 
                board_width = calib_args.board_width, 
                board_height = calib_args.board_height, 
                cam = calib_args.cam,
                API_cam = calib_args.API_cam, 
                width = calib_args.width, 
                height = calib_args.height):

    d = os.path.dirname(__file__)
    p = r'{}/Calibration_Images'.format(d)
    if not os.path.exists(p):
        os.makedirs(p)
    if int(mode) == 1:
        get_images(cam, API_cam, board_width, board_height, width, height)

    WAIT_TIME = 50
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    objp = np.zeros((board_height*board_width, 3), np.float32)
    objp[:,:2] = np.mgrid[0:board_width, 0:board_height].T.reshape(-1, 2)
    
    objp = objp*marker_size
    
    objpoints = [] 
    imgpoints = []
    
    print("----- CALIBRATION PROCESS -----")
    print(" ")
    
    images = glob.glob('Calibration_Images/*.jpg')
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (9,6), None)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray,corners, (11, 11), (-1, -1), criteria)
            imgpoints.append(corners2)
            img = cv2.drawChessboardCorners(img, (9, 6), corners2, ret)
            cv2.imshow('img', img)
            
            cv2.waitKey(WAIT_TIME)
            
    cv2.destroyAllWindows()
    
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
    
    print("Camera Matrix : " , mtx)
    print("Camera Distorsion : " , dist)
    
    cv_file = cv2.FileStorage("calib_params.yaml", cv2.FILE_STORAGE_WRITE)
    cv_file.write("mtx", mtx)
    cv_file.write("dist", dist)
    cv_file.write("dct", dct)
    cv_file.write("cam", cam)
    cv_file.write("API_cam", API_cam)
    cv_file.write("width", width)
    cv_file.write("height", height)
    cv_file.write("marker_size", marker_size)
    cv_file.release()
    
    print(" ")
    print("----- CALIBRATION SUCCESSFUL -----")
    
def angle(x_a, x_b, y_a, y_b):
    
    hip = math.sqrt((x_b - x_a)**2 + (y_b - y_a)**2)
    cat_a = x_b - x_a
    ang = np.degrees(math.acos(cat_a/hip))
    
    if y_b >= y_a :
        ang = -abs(ang)
    else:
        ang = abs(ang)
        
    return ang

def assign():
    size_in = 0
    font = cv2.FONT_HERSHEY_DUPLEX
    
    mtx, dist, dct, cam, API_cam, width, height, _ = read_calib()
    
    aruco_dict  = aruco.getPredefinedDictionary(eval('aruco.'+dct))
    parameters  = aruco.DetectorParameters_create()
    
    cap = cv2.VideoCapture(cam, API_cam)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    for i in range(100):
    
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters, cameraMatrix=mtx, distCoeff=dist)
    
        if np.all(ids != None):
            
            if(size_in <= len(ids)):
                robot_IDS = sorted(np.squeeze(ids).reshape(len(ids), 1))
                size_in = len(ids)
    
    robot_POSE = [[0]*3]*size_in
    
    print("----- ROBOTS DETECTION REPORT -----")
    
    for j in range (size_in):
        
        IDS = np.squeeze(np.squeeze(np.where(ids==robot_IDS[j]))[0])
        
        x_j = ((corners[IDS][-1][0][0]+
                corners[IDS][-1][1][0]+
                corners[IDS][-1][2][0]+
                corners[IDS][-1][3][0])/4)
        y_j = ((corners[IDS][-1][0][1]+
                corners[IDS][-1][1][1]+
                corners[IDS][-1][2][1]+
                corners[IDS][-1][3][1])/4)
        
        x_a = (corners[IDS][-1][0][0]+
               corners[IDS][-1][3][0])/2
        x_b = (corners[IDS][-1][1][0]+
               corners[IDS][-1][2][0])/2
        y_a = (corners[IDS][-1][0][1]+
               corners[IDS][-1][3][1])/2
        y_b = (corners[IDS][-1][1][1]+
               corners[IDS][-1][2][1])/2
               
        ang_j = angle(x_a, x_b, y_a, y_b)
               
        robot_POSE[j] = [x_j, y_j, ang_j]
     
    for k in range(size_in):
        cv2.putText(frame, ("ALPHA "+str(k)),
                   (int(robot_POSE[k][0]) + 20, int(robot_POSE[k][1]) - 60),
                   font, 0.5, (0,255,255), 2, cv2.LINE_AA)
        cv2.putText(frame, ("POSITION (" + str(robot_POSE[k][0]) + ", " + str(robot_POSE[k][1]) + ")"),
                   (int(robot_POSE[k][0])+20, int(robot_POSE[k][1]) - 40),
                   font, 0.5, (0,255,255), 2, cv2.LINE_AA)
        cv2.putText(frame, ("ANGLE " + str(robot_POSE[k][2]) + " (degrees)"),
                   (int(robot_POSE[k][0]) + 20, int(robot_POSE[k][1]) - 20),
                   font, 0.5, (0,255,255), 2, cv2.LINE_AA)
        cv2.circle(frame,(int(robot_POSE[k][0]), int(robot_POSE[k][1])), 30, (0,255,255), 4)
        cv2.circle(frame,(int(robot_POSE[k][0]), int(robot_POSE[k][1])), 10, (0,255,255), 2)
    
    cv2.imshow('frame', frame)
    
    print(" ")
    print("ArUco Markers based robot detection")
    print(" ")
    print("Number of markers detected --> "+str(size_in))
    print(" ")
    
    for k in range(size_in):
        print(str(robot_IDS[k])+" marker detected --> Assigned as robot unit: ALPHA "+str(k))
        print("ALPHA "+str(k)+" detected on X = "+str(robot_POSE[k][0])+" (pixels)")
        print("ALPHA "+str(k)+" detected on Y = "+str(robot_POSE[k][1])+" (pixels)")
        print("ALPHA "+str(k)+" detected with angle = "+str(robot_POSE[k][2])+" (degrees)")
        print(" ")
        
    cv2_file = cv2.FileStorage("robot_assign.yaml", cv2.FILE_STORAGE_WRITE)
    cv2_file.write("robot_IDS", np.array(robot_IDS))
    cv2_file.release()
    
    cv2.waitKey(10000)
    cv2.destroyAllWindows()
    cap.release()
    
def read_calib():
    cv_file = cv2.FileStorage("calib_params.yaml", cv2.FILE_STORAGE_READ)
    mtx = cv_file.getNode("mtx").mat()
    dist = cv_file.getNode("dist").mat()
    dct = cv_file.getNode("dct").string()
    cam = int(cv_file.getNode("cam").real())
    if cv_file.getNode("API_cam").isString() != True:
        API_cam = None
    else:
        API_cam = cv_file.getNode("API_cam").string()
    width = int(cv_file.getNode("width").real())
    height = int(cv_file.getNode("height").real())
    marker_size = cv_file.getNode("marker_size").real()
    cv_file.release()
    
    return mtx, dist, dct, cam, API_cam, width, height, marker_size

def initialize():   
    cv_file = cv2.FileStorage("robot_assign.yaml", cv2.FILE_STORAGE_READ)
    robot_IDS = cv_file.getNode("robot_IDS").mat()
    cv_file.release()
    
    size_in = len(robot_IDS)
    mtx, dist, dct, _, _, width, height, marker_size = read_calib()

    globals()['robot_POSE_A'] = [[0]*3]*size_in
    globals()['robot_POSE_B'] = [[0]*8]*size_in
    globals()['x_j'] = 0
    globals()['y_j'] = 0
    globals()['ang_j'] = 0
    globals()['x_k'] = 0
    globals()['y_k'] = 0
    globals()['z_k'] = 0
    globals()['x_jk'] = 0
    globals()['y_jk'] = 0
    globals()['roll_k'] = 0
    globals()['pitch_k'] = 0
    globals()['yaw_k'] = 0
    globals()['aruco_dict'] = aruco.getPredefinedDictionary(eval('aruco.'+dct))
    globals()['parameters'] = aruco.DetectorParameters_create()
    globals()['marker_size'] = marker_size
    globals()['width'] = width
    globals()['height'] = height
    globals()['wr'] = [0]*size_in
    globals()['wl'] = [0]*size_in
    globals()['ang_vel'] = [[0]*2]*size_in
    globals()['F'] = [[0]*2]*size_in
    
    return robot_IDS, size_in
    
def get_pose(gray = pose_args.gray,
             mode = pose_args.mode,
             mtx = pose_args.mtx,
             dist = pose_args.dist,
             robot_IDS = pose_args.robot_IDS,
             size_in = pose_args.size_in):
    
    global x_j, y_j, ang_j
    global x_k, y_k, z_k
    global x_jk, y_jk
    global roll_k, pitch_k, yaw_k
    global robot_POSE_A, robot_POSE_B
    global aruco_dict
    global parameters
    global marker_size

    corners, ids, rejected = aruco.detectMarkers(gray, aruco_dict, parameters=parameters, cameraMatrix=mtx, distCoeff=dist)
    
    if np.all(ids != None):
        
        if int(mode) == 1:
            for k in range (size_in):
                IDS = np.squeeze(np.squeeze(np.where(ids==robot_IDS[k]))[0])
                
                if (type(IDS) == np.int64):
                    
                    x_jk = ((corners[IDS][-1][0][0]+
                            corners[IDS][-1][1][0]+
                            corners[IDS][-1][2][0]+
                            corners[IDS][-1][3][0])/4)
                    y_jk = ((corners[IDS][-1][0][1]+
                            corners[IDS][-1][1][1]+
                            corners[IDS][-1][2][1]+
                            corners[IDS][-1][3][1])/4)
                    
                    rvec, tvec ,_ = aruco.estimatePoseSingleMarkers(corners, marker_size, mtx, dist)
                    x_k = tvec.ravel()[0]
                    y_k = tvec.ravel()[1]
                    z_k = tvec.ravel()[2]
                    roll_k = np.degrees(rvec.ravel()[0])
                    pitch_k = np.degrees(rvec.ravel()[1])
                    yaw_k = np.degrees(rvec.ravel()[2])
                    
                    robot_POSE_B[k] = [x_jk, y_jk, x_k, y_k, z_k, roll_k, pitch_k, yaw_k]
                    
            return robot_POSE_B
        
        elif int(mode) == 0:
            for j in range (size_in):
                IDS = np.squeeze(np.squeeze(np.where(ids==robot_IDS[j]))[0])
    
                if (type(IDS) == np.int64):
                        
                    x_j = ((corners[IDS][-1][0][0]+
                            corners[IDS][-1][1][0]+
                            corners[IDS][-1][2][0]+
                            corners[IDS][-1][3][0])/4)
                    y_j = ((corners[IDS][-1][0][1]+
                            corners[IDS][-1][1][1]+
                            corners[IDS][-1][2][1]+
                            corners[IDS][-1][3][1])/4)
                    
                    x_a = (corners[IDS][-1][0][0]+
                           corners[IDS][-1][3][0])/2
                    x_b = (corners[IDS][-1][1][0]+
                           corners[IDS][-1][2][0])/2
                    y_a = (corners[IDS][-1][0][1]+
                           corners[IDS][-1][3][1])/2
                    y_b = (corners[IDS][-1][1][1]+
                           corners[IDS][-1][2][1])/2
                           
                    ang_j = angle(x_a, x_b, y_a, y_b)
                    
                    robot_POSE_A[j] = [x_j, y_j, ang_j]
        
            return robot_POSE_A
        
        else:
             print("Pose parameter mode not valid")
             sys.exit(0)
        
    else:
        if int(mode) == 1:
            return robot_POSE_B
        elif int(mode) == 0:
            return robot_POSE_A
        else:
            print("Pose parameter mode not valid")
            sys.exit(0)

def draw_robots(frame = draw_args.frame,
                robot_POSE = draw_args.robot_POSE,
                robot_IDS = draw_args.robot_IDS,
                mode = draw_args.mode):
    
    global width
    global height
    
    font = cv2.FONT_HERSHEY_DUPLEX
    size_in = len(robot_IDS)
    
    if len(robot_POSE[0]) == 3:
        
        if mode == 0:
            
            color = (0, 255, 0)
            
            for k in range(size_in):
                
                cv2.line(frame, (int(robot_POSE[k][0]+30), int(robot_POSE[k][1])),
                        (int(robot_POSE[k][0]+50), int(robot_POSE[k][1])), color, 1)
                cv2.line(frame, (int(robot_POSE[k][0]-30), int(robot_POSE[k][1])),
                        (int(robot_POSE[k][0]-50), int(robot_POSE[k][1])), color, 1)
                cv2.line(frame, (int(robot_POSE[k][0]), int(robot_POSE[k][1]+30)),
                        (int(robot_POSE[k][0]), int(robot_POSE[k][1]+50)), color, 1)
                cv2.line(frame, (int(robot_POSE[k][0]), int(robot_POSE[k][1]-30)),
                        (int(robot_POSE[k][0]), int(robot_POSE[k][1]-50)), color, 1)
                
                cv2.putText(frame, ("ROBOT: Alpha "+str(k)),
                           (int(robot_POSE[k][0]) + 20, int(robot_POSE[k][1]) - 60),
                           font, 0.5, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ("POSITION: (" + str(robot_POSE[k][0]) + ", " + str(robot_POSE[k][1]) + ")"),
                           (int(robot_POSE[k][0])+20, int(robot_POSE[k][1]) - 40),
                           font, 0.5, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ("ANGLE: " + str(robot_POSE[k][2]) + " (degrees)"),
                           (int(robot_POSE[k][0]) + 20, int(robot_POSE[k][1]) - 20),
                           font, 0.5, color, 1, cv2.LINE_AA)
                cv2.circle(frame,(int(robot_POSE[k][0]), int(robot_POSE[k][1])), 25, color, 4)
                cv2.circle(frame,(int(robot_POSE[k][0]), int(robot_POSE[k][1])), 10, color, 2)
                
                cv2.rectangle(frame, (15, height-45), (300, height-75), (255, 255, 255), -1)
                cv2.rectangle(frame, (20, height-50), (60, height-70), color, -1)
                cv2.putText(frame, ("POSE PARAMETERS"), (70, height-55), font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                
        elif mode == 1:
            
            color = (0, 255, 255)
            
            for k in range(size_in):
                
                cv2.putText(frame, ("ROBOT: Alpha "+str(k)),
                           (20, int((k+1)*20)), font, 0.5, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ("--> X = " + str(robot_POSE[k][0]) + ", Y = " + str(robot_POSE[k][1])),
                           (170, int((k+1)*20)), font, 0.5, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ("--> Angle = " + str(round(robot_POSE[k][2], 2)) + " [degrees]"),
                           (440, int((k+1)*20)), font, 0.5, color, 1, cv2.LINE_AA)
                
                cv2.circle(frame,(int(robot_POSE[k][0]), int(robot_POSE[k][1])), 10, color, 2)
                cv2.circle(frame,(int(robot_POSE[k][0]), int(robot_POSE[k][1])), 25, color, 4)
                
                p1A = [robot_POSE[k][0]+30*math.cos(math.radians(robot_POSE[k][2])),
                       robot_POSE[k][1]-30*math.sin(math.radians(robot_POSE[k][2]))]
                p1B = [robot_POSE[k][0]+60*math.cos(math.radians(robot_POSE[k][2])),
                       robot_POSE[k][1]-60*math.sin(math.radians(robot_POSE[k][2]))]
                
                p2A = [robot_POSE[k][0]-30*math.sin(math.radians(robot_POSE[k][2])),
                       robot_POSE[k][1]-30*math.cos(math.radians(robot_POSE[k][2]))]
                p2B = [robot_POSE[k][0]-50*math.sin(math.radians(robot_POSE[k][2])),
                       robot_POSE[k][1]-50*math.cos(math.radians(robot_POSE[k][2]))]
                
                p3A = [robot_POSE[k][0]+30*math.sin(math.radians(robot_POSE[k][2])),
                       robot_POSE[k][1]+30*math.cos(math.radians(robot_POSE[k][2]))]
                p3B = [robot_POSE[k][0]+50*math.sin(math.radians(robot_POSE[k][2])),
                       robot_POSE[k][1]+50*math.cos(math.radians(robot_POSE[k][2]))]
                
                cv2.line(frame, (int(p1A[0]), int(p1A[1])), (int(p1B[0]), int(p1B[1])), color, 2)
                cv2.line(frame, (int(p2A[0]), int(p2A[1])), (int(p2B[0]), int(p2B[1])), color, 2)
                cv2.line(frame, (int(p3A[0]), int(p3A[1])), (int(p3B[0]), int(p3B[1])), color, 2)
                
                cv2.rectangle(frame, (15, height-45), (300, height-75), (255, 255, 255), -1)
                cv2.rectangle(frame, (20, height-50), (60, height-70), color, -1)
                cv2.putText(frame, ("POSE PARAMETERS"), (70, height-55), font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                
        else:
            print("Drawn parameter mode not valid")
            sys.exit(0)
            
    else:
        if mode == 0:
            
            color = (0, 255, 0)
            
            for k in range(size_in):
                
                cv2.line(frame, (int(robot_POSE[k][0]+30), int(robot_POSE[k][1])),
                        (int(robot_POSE[k][0]+50), int(robot_POSE[k][1])), color, 1)
                cv2.line(frame, (int(robot_POSE[k][0]-30), int(robot_POSE[k][1])),
                        (int(robot_POSE[k][0]-50), int(robot_POSE[k][1])), color, 1)
                cv2.line(frame, (int(robot_POSE[k][0]), int(robot_POSE[k][1]+30)),
                        (int(robot_POSE[k][0]), int(robot_POSE[k][1]+50)), color, 1)
                cv2.line(frame, (int(robot_POSE[k][0]), int(robot_POSE[k][1]-30)),
                        (int(robot_POSE[k][0]), int(robot_POSE[k][1]-50)), color, 1)
                
                cv2.putText(frame, ("ROBOT: Alpha "+str(k)),
                           (int(robot_POSE[k][0]) + 20, int(robot_POSE[k][1]) - 60),
                           font, 0.5, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ("POSITION: (" + str(round(robot_POSE[k][2],2)) + ", " + str(round(robot_POSE[k][3],2)) + ", " + str(round(robot_POSE[k][4],2)) + ") [meters]"),
                           (int(robot_POSE[k][0])+20, int(robot_POSE[k][1]) - 40),
                           font, 0.5, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ("ANGLE: " + str(round(robot_POSE[k][6],2)) + ", " + str(round(robot_POSE[k][7],2)) + ", " + str(round(robot_POSE[k][5],2)) + " (deg)"),
                           (int(robot_POSE[k][0]) + 20, int(robot_POSE[k][1]) - 20),
                           font, 0.5, color, 1, cv2.LINE_AA)
                cv2.circle(frame,(int(robot_POSE[k][0]), int(robot_POSE[k][1])), 25, color, 4)
                cv2.circle(frame,(int(robot_POSE[k][0]), int(robot_POSE[k][1])), 10, color, 2)
                
                cv2.rectangle(frame, (15, height-45), (300, height-75), (255, 255, 255), -1)
                cv2.rectangle(frame, (20, height-50), (60, height-70), color, -1)
                cv2.putText(frame, ("POSE PARAMETERS"), (70, height-55), font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        
        elif mode == 1:
            
            color = (0, 255, 255)
            
            for k in range(size_in):
                
                cv2.putText(frame, ("ROBOT: Alpha "+str(k)),
                           (20, int((k+1)*20)), font, 0.5, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ("--> X = " + str(round(robot_POSE[k][2],2)) + ", Y = " + str(round(robot_POSE[k][3],2)) + ", Z = " + str(round(robot_POSE[k][4],2))+ " [meters]"),
                           (170, int((k+1)*20)), font, 0.5, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ("--> Roll = " + str(round(robot_POSE[k][6],2)) + ", Pitch = " + str(round(robot_POSE[k][7],2)) + ", Yaw = " + str(round(robot_POSE[k][5],2))+ " [deg]"),
                           (560, int((k+1)*20)), font, 0.5, color, 1, cv2.LINE_AA)
                
                cv2.circle(frame,(int(robot_POSE[k][0]), int(robot_POSE[k][1])), 10, color, 2)
                cv2.circle(frame,(int(robot_POSE[k][0]), int(robot_POSE[k][1])), 25, color, 4)
                
                p1A = [robot_POSE[k][0]-30*math.cos(math.radians(robot_POSE[k][5])),
                       robot_POSE[k][1]+30*math.sin(math.radians(robot_POSE[k][5]))]
                p1B = [robot_POSE[k][0]-60*math.cos(math.radians(robot_POSE[k][5])),
                       robot_POSE[k][1]+60*math.sin(math.radians(robot_POSE[k][5]))]
                
                p2A = [robot_POSE[k][0]+30*math.sin(math.radians(robot_POSE[k][5])),
                       robot_POSE[k][1]+30*math.cos(math.radians(robot_POSE[k][5]))]
                p2B = [robot_POSE[k][0]+50*math.sin(math.radians(robot_POSE[k][5])),
                       robot_POSE[k][1]+50*math.cos(math.radians(robot_POSE[k][5]))]
                
                p3A = [robot_POSE[k][0]-30*math.sin(math.radians(robot_POSE[k][5])),
                       robot_POSE[k][1]-30*math.cos(math.radians(robot_POSE[k][5]))]
                p3B = [robot_POSE[k][0]-50*math.sin(math.radians(robot_POSE[k][5])),
                       robot_POSE[k][1]-50*math.cos(math.radians(robot_POSE[k][5]))]
                
                cv2.line(frame, (int(p1A[0]), int(p1A[1])), (int(p1B[0]), int(p1B[1])), color, 2)
                cv2.line(frame, (int(p2A[0]), int(p2A[1])), (int(p2B[0]), int(p2B[1])), color, 2)
                cv2.line(frame, (int(p3A[0]), int(p3A[1])), (int(p3B[0]), int(p3B[1])), color, 2)
                
                cv2.rectangle(frame, (15, height-45), (300, height-75), (255, 255, 255), -1)
                cv2.rectangle(frame, (20, height-50), (60, height-70), color, -1)
                cv2.putText(frame, ("POSE PARAMETERS"), (70, height-55), font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                
        else:
            print("Drawn parameter mode not valid")
            sys.exit(0)
            
def MIMC_VADOC_single(robot_POSE, robot_GOAL, ctr_params):
    
    #-- MIMC-VADOC CONTROLLER--------------------------------------------------
    
    #-- Controller input parameters
    x = robot_POSE[0]
    y = robot_POSE[1]
    ang = math.radians(robot_POSE[2])
    x_d = robot_GOAL[0]
    y_d = robot_GOAL[1]
    ang_d = math.radians(robot_GOAL[2])
    r = ctr_params[0]
    l = ctr_params[1]
    ks = ctr_params[2]
    d0 = ctr_params[3]
    kw = ctr_params[4]
    U_max = ctr_params[5]
    
    #-- MIMC MODEL
    #-- Distance toward objetive
    d_m = ((x_d - x)**2 + (y_d - y)**2)**(1/2)
    
    #-- Attraction field pre-compensation
    if d_m < 30 :
        d0 = d0*2
    else:
        d0 = ctr_params[3]
        
    #-- Attraction field calculations
    if d_m <= d0:
        Fa = [0, 0]
    else:
        Ks = ks/((d_m)**(1/2))
        Fa = [Ks*(d_m - d0)*((x_d - x)/d_m), -Ks*(d_m - d0)*((y_d - y)/d_m)]
    
    #-- Attraction field vector
    F = [Fa[0], Fa[1]]
    
    #-- Linear velocities calculation
    o = np.array([math.cos(ang), math.sin(ang)])
    F_f = np.array([[F[0]/(1+(F[0]**2+F[1]**2)**(1/2))], [F[1]/(1+(F[0]**2+F[1]**2)**(1/2))]])
    
    #-- Final maximum based linear velocity calculation
    if o @ F_f >= 0:
        ui = (o @ F_f)*U_max
    else:
        ui = 0
        
    
    #-- VADOC MODEL
    #-- Angle to objetive direction compensation
    F_ang = math.acos((x_d - x)/d_m)
    if y_d >= y:
        F_ang = -abs(F_ang)
    else:
        F_ang = abs(F_ang)     
    ang_F = F_ang
    
    #-- Current angle vector
    x_dist = np.cos(ang)
    y_dist = np.sin(ang)
    
    #-- Objetive vector
    x_dist_F = np.cos(F_ang)
    y_dist_F = np.sin(F_ang)
    
    #-- Final desired vector
    x_des = np.cos(ang_d)
    y_des = np.sin(ang_d)
    
    #-- Virtual angle distance toward objetive
    F_dist = ((x_dist_F - x_dist)**2 + (y_dist_F - y_dist)**2)**(1/2)
    
    #-- Virtual angle distance toward final desired angle
    F_dist_des = ((x_des - x_dist)**2 + (y_des - y_dist)**2)**(1/2)
    
    #-- Angle direction parameters
    wi_h = ang - ang_F
    wi_ang = ang - ang_d
    
    #-- Angular velocities singularities compensations
    if d_m <= d0:
        
        #-- Final angle based singularities compensations
        if (ang>np.radians(90) and ang_d<np.radians(-90)) or (ang<np.radians(-90) and ang_d>np.radians(90)):
            if wi_ang >= 0:
                wi = -kw*F_dist_des
            else:
                wi = kw*F_dist_des
        else:
            if wi_ang >= 0:
                wi = kw*F_dist_des
            else:
                wi = -kw*F_dist_des
    else:
        
        #-- Objetive angle based singularities compensations
        if (ang>np.radians(90) and ang_F<np.radians(-90)) or (ang<np.radians(-90) and ang_F>np.radians(90)):
            if wi_h >= 0:
                wi = -kw*F_dist
            else:
                wi = kw*F_dist
        else:
            if wi_h >= 0:
                wi = kw*F_dist
            else:
                wi = -kw*F_dist
    
    #-- Tranform base velocity parameters to dynamical actuator signals
    wl = float(np.squeeze((ui + ((wi*l)/2))*(1/(r))))
    wr = float(np.squeeze((ui - ((wi*l)/2))*(1/(r))))
        
    #--------------------------------------------------------------------------
    
    return wl, wr, F

def MIMC_VADOC_multiple(robot_POSE, robot_IDS, robot_GOAL, ctr_params):
    
    global wr
    global wl
    global F
    
    size_in = len(robot_IDS)
    
    #-- MIMC-VADOC CONTROLLER--------------------------------------------------
    
    #-- Controller input parameters
    r = ctr_params[0]
    l = ctr_params[1]
    ks = ctr_params[2]
    d0 = ctr_params[3]
    kw = ctr_params[4]
    U_max = ctr_params[5]
    kr = ctr_params[6]
    L0 = ctr_params[7]
    
    for k in range(size_in):
        
        #-- MIMC MODEL
        
        x = robot_POSE[k][0]
        y = robot_POSE[k][1]
        ang = math.radians(robot_POSE[k][2])
        x_d = robot_GOAL[k][0]
        y_d = robot_GOAL[k][1]
        ang_d = math.radians(robot_GOAL[k][2])
    
        #-- Distance toward objetive
        d_m = ((x_d - x)**2 + (y_d - y)**2)**(1/2)
        
        #-- Attraction field pre-compensation
        if d_m < d0 :
            d0 = 30
        else:
            d0 = ctr_params[3]
            
        #-- Attraction field calculations
        if d_m <= d0:
            Fa = [0, 0]
        else:
            Ks = ks/((d_m)**(1/2))
            Fa = [Ks*(d_m - d0)*((x_d - x)/d_m), -Ks*(d_m - d0)*((y_d - y)/d_m)]
        
        #-- Repulsion field calculations
        Fr = [0, 0]
        R_POSE = np.delete(robot_POSE, k, axis=0)
        for i in range(size_in - 1):
            Rx_d = R_POSE[i][0]
            Ry_d = R_POSE[i][1]
            L_obs = (((Rx_d-x)**2)*1.2+(Ry_d-y)**2)**(1/2)
            if L_obs <= L0:
                rep = [((kr/(L_obs**3))*((1/L_obs)-(1/L0))*(Rx_d-x)), -((kr/(L_obs**3))*((1/L_obs)-(1/L0))*(Ry_d-y))]
            else:
                rep = [0, 0]      
            Fr = Fr + rep

        #-- Potential field vector
        F[k] = [Fa[0]-Fr[0], Fa[1]-Fr[1]]
        
        #-- Linear velocities calculation
        o = np.array([math.cos(ang), math.sin(ang)])
        F_f = np.array([[F[k][0]/(1+(F[k][0]**2+F[k][1]**2)**(1/2))], [F[k][1]/(1+(F[k][0]**2+F[k][1]**2)**(1/2))]])
        
        #-- Final maximum based linear velocity calculation
        if o @ F_f >= 0:
            ui = (o @ F_f)*U_max
        else:
            ui = 0
        
        #-- VADOC MODEL
        
        #-- Angle to objetive direction compensation
        F_ang = math.acos((x_d - x)/d_m)
        if y_d >= y:
            F_ang = -abs(F_ang)
        else:
            F_ang = abs(F_ang)     
        ang_F = F_ang      
        
        #-- Current angle vector
        x_dist = np.cos(ang)
        y_dist = np.sin(ang)
        
        #-- Objetive vector
        x_dist_F = np.cos(ang_F)
        y_dist_F = np.sin(ang_F)
        
        #-- Final desired vector
        x_des = np.cos(ang_d)
        y_des = np.sin(ang_d)
        
        #-- Virtual angle distance toward objetive
        F_dist = ((x_dist_F - x_dist)**2 + (y_dist_F - y_dist)**2)**(1/2)
        
        #-- Virtual angle distance toward final desired angle
        F_dist_des = ((x_des - x_dist)**2 + (y_des - y_dist)**2)**(1/2)
        
        #-- Angle direction parameters
        wi_h = ang - ang_F
        wi_ang = ang - ang_d
        
        #-- Angular velocities singularities compensations
        if d_m <= d0:
            
            #-- Final angle based singularities compensations
            if (ang>np.radians(90) and ang_d<np.radians(-90)) or (ang<np.radians(-90) and ang_d>np.radians(90)):
                if wi_ang >= 0:
                    wi = -kw*F_dist_des
                else:
                    wi = kw*F_dist_des
            else:
                if wi_ang >= 0:
                    wi = kw*F_dist_des
                else:
                    wi = -kw*F_dist_des
        else:
            
            #-- Objetive angle based singularities compensations
            if (ang>np.radians(90) and ang_F<np.radians(-90)) or (ang<np.radians(-90) and ang_F>np.radians(90)):
                if wi_h >= 0:
                    wi = -kw*F_dist
                else:
                    wi = kw*F_dist
            else:
                if wi_h >= 0:
                    wi = kw*F_dist
                else:
                    wi = -kw*F_dist
        
        #-- Angular velocities singularities compensations
        if d_m <= d0:
            wi = kw*F_dist_des*np.sign(ang - ang_d)
        else:
            wi = kw*F_dist*np.sign(ang - ang_F)
        
        #-- Tranform base velocity parameters to dynamical actuator signals
        wl[k] = float(np.squeeze((ui + ((wi*l)/2))*(1/(r))))
        wr[k] = float(np.squeeze((ui - ((wi*l)/2))*(1/(r))))
            
        #----------------------------------------------------------------------
        
def MIMC_VADOC_multiple_2(robot_POSE, robot_IDS, robot_GOAL, ctr_params):
    
    global wr
    global wl
    global F
    
    size_in = len(robot_IDS)
    
    #-- MIMC-VADOC CONTROLLER--------------------------------------------------
    
    #-- Controller input parameters
    r = ctr_params[0]
    l = ctr_params[1]
    ks = ctr_params[2]
    d0 = ctr_params[3]
    kw = ctr_params[4]
    U_max = ctr_params[5]
    kr = ctr_params[6]
    L0 = ctr_params[7]
    
    for k in range(size_in):
        
        #-- MIMC MODEL
        
        x = robot_POSE[k][0]
        y = robot_POSE[k][1]
        ang = math.radians(robot_POSE[k][2])
        x_d = robot_GOAL[k][0]
        y_d = robot_GOAL[k][1]
        ang_d = math.radians(robot_GOAL[k][2])
    
        #-- Distance toward objetive
        d_m = ((x_d - x)**2 + (y_d - y)**2)**(1/2)
        
        #-- Attraction field pre-compensation
        if d_m < d0 :
            d0 = 30
        else:
            d0 = ctr_params[3]
            
        #-- Attraction field calculations
        if d_m <= d0:
            Fa = [0, 0]
        else:
            Ks = ks/((d_m)**(1/2))
            Fa = [Ks*(d_m - d0)*((x_d - x)/d_m), -Ks*(d_m - d0)*((y_d - y)/d_m)]
        
        #-- Repulsion field calculations
        Fr = [0, 0]
        R_POSE = np.delete(robot_POSE, k, axis=0)
        for i in range(size_in - 1):
            Rx_d = R_POSE[i][0]
            Ry_d = R_POSE[i][1]
            L_obs = (((Rx_d-x)**2)*1.2+(Ry_d-y)**2)**(1/2)
            if L_obs <= L0:
                rep = [((kr/(L_obs**3))*((1/L_obs)-(1/L0))*(Rx_d-x)), -((kr/(L_obs**3))*((1/L_obs)-(1/L0))*(Ry_d-y))]
            else:
                rep = [0, 0]      
            Fr = Fr + rep

        #-- Potential field vector
        F[k] = [Fa[0]-Fr[0], Fa[1]-Fr[1]]
        
        #-- Linear velocities calculation
        o = np.array([math.cos(ang), math.sin(ang)])
        F_f = np.array([[F[k][0]/(1+(F[k][0]**2+F[k][1]**2)**(1/2))], [F[k][1]/(1+(F[k][0]**2+F[k][1]**2)**(1/2))]])
        
        #-- Final maximum based linear velocity calculation
        if o @ F_f >= 0:
            ui = (o @ F_f)*U_max
        else:
            ui = 0
        
        #-- VADOC MODEL
        
        #-- Angle to objetive direction compensation
        #ang_F = math.atan((y_d - y)/(x_d - x))
        ang_F = math.atan2((-(y_d - y)),(x_d - x))
        print(ang)
        print(ang_F)
        #F_ang = math.acos((x_d - x)/d_m)
        
        '''
        if y_d >= y:
            F_ang = -abs(F_ang)
        else:
            F_ang = abs(F_ang)     
        ang_F = F_ang
        '''
        #-- Current angle vector
        x_dist = np.cos(ang)
        y_dist = np.sin(ang)
        
        #-- Objetive vector
        x_dist_F = np.cos(ang_F)
        y_dist_F = np.sin(ang_F)
        
        #-- Final desired vector
        x_des = np.cos(ang_d)
        y_des = np.sin(ang_d)
        
        #-- Virtual angle distance toward objetive
        F_dist = ((x_dist_F - x_dist)**2 + (y_dist_F - y_dist)**2)**(1/2)
        
        #-- Virtual angle distance toward final desired angle
        F_dist_des = ((x_des - x_dist)**2 + (y_des - y_dist)**2)**(1/2)
        
        '''
        #-- Angular velocities singularities compensations
        if d_m <= d0:
            
            #-- Final angle based singularities compensations
            if (ang>np.radians(90) and ang_d<np.radians(-90)) or (ang<np.radians(-90) and ang_d>np.radians(90)):
                if wi_ang >= 0:
                    wi = -kw*F_dist_des
                else:
                    wi = kw*F_dist_des
            else:
                if wi_ang >= 0:
                    wi = kw*F_dist_des
                else:
                    wi = -kw*F_dist_des
        else:
            
            #-- Objetive angle based singularities compensations
            if (ang>np.radians(90) and ang_F<np.radians(-90)) or (ang<np.radians(-90) and ang_F>np.radians(90)):
                if wi_h >= 0:
                    wi = -kw*F_dist
                else:
                    wi = kw*F_dist
            else:
                if wi_h >= 0:
                    wi = kw*F_dist
                else:
                    wi = -kw*F_dist
        '''
        #-- Angular velocities singularities compensations
        if d_m <= d0:
            wi = kw*F_dist_des*np.sign(ang - ang_d)
            if (ang_d>math.pi/2 and ang<-math.pi/2) or (ang>math.pi/2 and ang_d<-math.pi/2):
                wi = -wi
        else:
            wi = kw*F_dist*np.sign(ang - ang_F)
            if (ang_F>math.pi/2 and ang<-math.pi/2) or (ang>math.pi/2 and ang_F<-math.pi/2):
                wi = -wi
            
        
        
        #-- Tranform base velocity parameters to dynamical actuator signals
        wl[k] = float(np.squeeze((ui + ((wi*l)/2))*(1/(r))))
        wr[k] = float(np.squeeze((ui - ((wi*l)/2))*(1/(r))))
            
        #----------------------------------------------------------------------
    
def trdiff_control_single(frame = ctrdiff_args.frame,
                          robot_POSE = ctrdiff_args.robot_POSE,
                          robot_IDS = ctrdiff_args.robot_IDS,
                          robot_GOAL = ctrdiff_args.robot_GOAL,
                          ctr_mode = ctrdiff_args.ctr_mode,
                          ctr_params = ctrdiff_args.ctr_params):
    
    global width
    global height
    
    font = cv2.FONT_HERSHEY_DUPLEX
    robot_POSE = np.squeeze(robot_POSE)
    color = (255, 0, 0)
    
    if len(robot_POSE[0]) == 3:
        
        if len(robot_IDS) == 1:
            
            if str(ctr_mode) == "MIMC-VADOC":
            
                wl, wr, F = MIMC_VADOC_single(robot_POSE, robot_GOAL, ctr_params)
                
                x = robot_POSE[0]
                y = robot_POSE[1]
                x_d = robot_GOAL[0]
                y_d = robot_GOAL[1]
                ang_d = math.radians(robot_GOAL[2])
                
                cv2.arrowedLine(frame, (int(x), int(y)), (int(x+(0.5*F[0])), int(y+(0.5*-F[1]))), color, 3)
                cv2.circle(frame, (int(x_d), int(y_d)), 5, color, 1)
                
                cv2.putText(frame, ("GOAL COORDINATES"), (int(x_d) + 20, int(y_d) - 40), font, 0.4, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ((str(x_d)) + ", " + str(y_d) + ", " + str(round(math.degrees(ang_d), 2))), (int(x_d)+20, int(y_d) - 20), font, 0.4, color, 1, cv2.LINE_AA)
                
                cv2.line(frame, (int(x_d+30), int(y_d)), (int(x_d+50), int(y_d)), color, 1)
                cv2.line(frame, (int(x_d-30), int(y_d)), (int(x_d-50), int(y_d)), color, 1)
                cv2.line(frame, (int(x_d), int(y_d+30)), (int(x_d), int(y_d+50)), color, 1)
                cv2.line(frame, (int(x_d), int(y_d-30)), (int(x_d), int(y_d-50)), color, 1)
                
                p1 = [robot_POSE[0]-40*math.sin(math.radians(robot_POSE[2])),
                      robot_POSE[1]-40*math.cos(math.radians(robot_POSE[2]))]
                p2 = [robot_POSE[0]+40*math.sin(math.radians(robot_POSE[2])),
                      robot_POSE[1]+40*math.cos(math.radians(robot_POSE[2]))]
                
                if wl <= 0:
                    p1A = [p1[0]-20*math.cos(math.radians(robot_POSE[2])),
                           p1[1]+20*math.sin(math.radians(robot_POSE[2]))]
                    p1B = [p1[0]-60*math.cos(math.radians(robot_POSE[2])),
                           p1[1]+60*math.sin(math.radians(robot_POSE[2]))]
                else:
                    p1A = [p1[0]+20*math.cos(math.radians(robot_POSE[2])),
                           p1[1]-20*math.sin(math.radians(robot_POSE[2]))]
                    p1B = [p1[0]+60*math.cos(math.radians(robot_POSE[2])),
                           p1[1]-60*math.sin(math.radians(robot_POSE[2]))]
                
                if wr <= 0:
                    p2A = [p2[0]-20*math.cos(math.radians(robot_POSE[2])),
                           p2[1]+20*math.sin(math.radians(robot_POSE[2]))]
                    p2B = [p2[0]-60*math.cos(math.radians(robot_POSE[2])),
                           p2[1]+60*math.sin(math.radians(robot_POSE[2]))]
                else:
                    p2A = [p2[0]+20*math.cos(math.radians(robot_POSE[2])),
                           p2[1]-20*math.sin(math.radians(robot_POSE[2]))]
                    p2B = [p2[0]+60*math.cos(math.radians(robot_POSE[2])),
                           p2[1]-60*math.sin(math.radians(robot_POSE[2]))]
                    
                cv2.arrowedLine(frame, (int(p1A[0]), int(p1A[1])), (int(p1B[0]), int(p1B[1])), color, 2) 
                cv2.arrowedLine(frame, (int(p2A[0]), int(p2A[1])), (int(p2B[0]), int(p2B[1])), color, 2)
                
                cv2.putText(frame, ("Required angular velocities"),
                           (int(robot_POSE[0]) + 40, int(robot_POSE[1]) + 40),
                           font, 0.5, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ("wi = " + str(round(wl, 2)) + ", wr = " + str(round(wr, 2))),
                           (int(robot_POSE[0]) + 40, int(robot_POSE[1]) + 60),
                           font, 0.5, color, 1, cv2.LINE_AA)
                
                cv2.rectangle(frame, (15, height-15), (300, height-45), (255, 255, 255), -1)
                cv2.rectangle(frame, (20, height-20), (60, height-40), color, -1)
                cv2.putText(frame, ("CONTROLLER PARAMETERS"), (70, height-25), font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                
                return [wr, wl]
            
            elif str(ctr_mode) == "DYNAMIC-FEEDBACK":
                print("DYNAMIC-FEEDBACK controller is on working")
                sys.exit(0)
                
            else:
                print("Non-existent controller mode command")
                sys.exit(0)
            
        else:
            print("Single controllers for differential robots do not support multiple units")
            sys.exit(0)
    
    else:
        print("Single controllers for differential robots only support pixel based pose estimation")
        sys.exit(0)
        
def trdiff_control_multiple(frame = ctrdiff_args.frame,
                            robot_POSE = ctrdiff_args.robot_POSE,
                            robot_IDS = ctrdiff_args.robot_IDS,
                            robot_GOAL = ctrdiff_args.robot_GOAL,
                            ctr_mode = ctrdiff_args.ctr_mode,
                            ctr_params = ctrdiff_args.ctr_params):
    
    global wr
    global wl
    global F
    global width
    global height
    global ang_vel
    
    font = cv2.FONT_HERSHEY_DUPLEX
    robot_POSE = np.squeeze(robot_POSE)
    color = (255, 0, 0)
    size_in = len(robot_IDS)
        
    if len(robot_POSE[0]) == 3:
        
        if str(ctr_mode) == "MIMC-VADOC":
        
            MIMC_VADOC_multiple_2(robot_POSE, robot_IDS, robot_GOAL, ctr_params)
            
            for k in range(size_in):
                
                ang_vel[k] = [wl[k], wr[k]]
            
                x = robot_POSE[k][0]
                y = robot_POSE[k][1]
                x_d = robot_GOAL[k][0]
                y_d = robot_GOAL[k][1]
                ang_d = math.radians(robot_GOAL[k][2])
                
                cv2.arrowedLine(frame, (int(x), int(y)), (int(x+(0.5*F[k][0])), int(y+(0.5*-F[k][1]))), color, 3)
                cv2.circle(frame, (int(x_d), int(y_d)), 5, color, 1)
                
                cv2.putText(frame, ("GOAL COORDINATES"), (int(x_d) + 20, int(y_d) - 40), font, 0.4, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ((str(x_d)) + ", " + str(y_d) + ", " + str(round(math.degrees(ang_d), 2))), (int(x_d)+20, int(y_d) - 20), font, 0.4, color, 1, cv2.LINE_AA)
                
                cv2.line(frame, (int(x_d+30), int(y_d)), (int(x_d+50), int(y_d)), color, 1)
                cv2.line(frame, (int(x_d-30), int(y_d)), (int(x_d-50), int(y_d)), color, 1)
                cv2.line(frame, (int(x_d), int(y_d+30)), (int(x_d), int(y_d+50)), color, 1)
                cv2.line(frame, (int(x_d), int(y_d-30)), (int(x_d), int(y_d-50)), color, 1)
                
                p1 = [robot_POSE[k][0]-40*math.sin(math.radians(robot_POSE[k][2])),
                      robot_POSE[k][1]-40*math.cos(math.radians(robot_POSE[k][2]))]
                p2 = [robot_POSE[k][0]+40*math.sin(math.radians(robot_POSE[k][2])),
                      robot_POSE[k][1]+40*math.cos(math.radians(robot_POSE[k][2]))]
                
                if wl[k] <= 0:
                    p1A = [p1[0]-20*math.cos(math.radians(robot_POSE[k][2])),
                           p1[1]+20*math.sin(math.radians(robot_POSE[k][2]))]
                    p1B = [p1[0]-60*math.cos(math.radians(robot_POSE[k][2])),
                           p1[1]+60*math.sin(math.radians(robot_POSE[k][2]))]
                else:
                    p1A = [p1[0]+20*math.cos(math.radians(robot_POSE[k][2])),
                           p1[1]-20*math.sin(math.radians(robot_POSE[k][2]))]
                    p1B = [p1[0]+60*math.cos(math.radians(robot_POSE[k][2])),
                           p1[1]-60*math.sin(math.radians(robot_POSE[k][2]))]
                
                if wr[k] <= 0:
                    p2A = [p2[0]-20*math.cos(math.radians(robot_POSE[k][2])),
                           p2[1]+20*math.sin(math.radians(robot_POSE[k][2]))]
                    p2B = [p2[0]-60*math.cos(math.radians(robot_POSE[k][2])),
                           p2[1]+60*math.sin(math.radians(robot_POSE[k][2]))]
                else:
                    p2A = [p2[0]+20*math.cos(math.radians(robot_POSE[k][2])),
                           p2[1]-20*math.sin(math.radians(robot_POSE[k][2]))]
                    p2B = [p2[0]+60*math.cos(math.radians(robot_POSE[k][2])),
                           p2[1]-60*math.sin(math.radians(robot_POSE[k][2]))]
                    
                cv2.arrowedLine(frame, (int(p1A[0]), int(p1A[1])), (int(p1B[0]), int(p1B[1])), color, 2) 
                cv2.arrowedLine(frame, (int(p2A[0]), int(p2A[1])), (int(p2B[0]), int(p2B[1])), color, 2)
                
                cv2.putText(frame, ("Required angular velocities"),
                           (int(robot_POSE[k][0]) + 40, int(robot_POSE[k][1]) + 40),
                           font, 0.5, color, 1, cv2.LINE_AA)
                cv2.putText(frame, ("wl = " + str(round(wl[k], 2)) + ", wr = " + str(round(wr[k], 2))),
                           (int(robot_POSE[k][0]) + 40, int(robot_POSE[k][1]) + 60),
                           font, 0.5, color, 1, cv2.LINE_AA)
                
                cv2.rectangle(frame, (15, height-15), (300, height-45), (255, 255, 255), -1)
                cv2.rectangle(frame, (20, height-20), (60, height-40), color, -1)
                cv2.putText(frame, ("CONTROLLER PARAMETERS"), (70, height-25), font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                
            return ang_vel
        
        elif str(ctr_mode) == "DYNAMIC-FEEDBACK":
            print("DYNAMIC-FEEDBACK controller is on working")
            sys.exit(0)
            
        else:
            print("Non-existent controller mode command")
            sys.exit(0)
        
    else:
        print("Multiple controllers for differential robots only support pixel based pose estimation")
        sys.exit(0)
    

def initialize_UDP(robot_IDS = UDP_com_args.robot_IDS,
                   host = UDP_com_args.host,
                   port = UDP_com_args.port,
                   robot_PC_IP = UDP_com_args.robot_PC_IP,
                   mode = UDP_com_args.mode):
    
    size_in = len(robot_IDS)
    globals()['UDP_IPS'] = [0]*size_in
    globals()['UDP_payload'] = [0]*size_in
    globals()['PC_IPS'] = [0]
    globals()['sock'] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    global UDP_IPS
    global UDP_payload
    global PC_IPS
    global sock
    
    sock.bind((host, port))
    
    if str(mode) == 'DIRECT':
        
        for k in range(size_in):
            UDP_IPS[k] = (robot_PC_IP[k], port)
            UDP_payload[k] = "/0,0n"

        print("DIRECT UDP mode connection selected")
    
    elif str(mode) == 'MASTER':
        
        size_in = len(robot_PC_IP)
        PC_IPS = PC_IPS*size_in
        globals()['UDP_payload_PC'] = [0]*size_in
        
        global UDP_payload_PC
        
        for k in range(size_in):
            PC_IPS[k] = (robot_PC_IP[k], port)
            UDP_payload_PC[k] = "/0,0,0n"
            
        print("MASTER UDP mode connection selected")
            
    elif str(mode) == 'LISTENER':
        
        if size_in == 1: 
            for k in range(size_in):
                UDP_IPS[k] = (robot_PC_IP[k], port)
                UDP_payload[k] = "/0,0n"
        else:
            print("LISTENER mode is only available for one robot connection")
            sys.exit(0)
        
        print("LISTENER UDP mode connection selected")
        
    else:
        print("Non-existent UDP connection mode command")
        sys.exit(0)

def transmission_UDP(mode = UDP_transmission_args.mode,
                     tr_data = UDP_transmission_args.tr_data):
    
    global UDP_IPS
    global UDP_payload
    global UDP_payload_PC
    global PC_IPS
    global sock
    
    if str(mode) == 'DIRECT':
        
        size_in = len(UDP_payload)
        
        for k in range(size_in):
            
            if int(tr_data[k][0]) > 255:
                tr_data[k][0] = 255
            if int(tr_data[k][0]) < -255:
                tr_data[k][0] = -255
            if int(tr_data[k][1]) > 255:
                tr_data[k][1] = 255
            if int(tr_data[k][1]) < -255:
                tr_data[k][1] = -255
            
            UDP_payload[k] = '/'+str(int(tr_data[k][0]))+','+str(int(tr_data[k][1]))+'n'

        for k in range(size_in):
            
            try:
                sock.sendto(bytes(UDP_payload[k], "utf-8"), UDP_IPS[k])
                #print("Message sent to robot IP: "+str(UDP_IPS[k]))
            except:
                pass
     
    elif str(mode) == 'MASTER':
        
        size_in = len(UDP_payload_PC)
        
        for k in range(size_in):
            
            UDP_payload_PC[k] = '/'+str(round(tr_data[k][0],2))+','+str(round(tr_data[k][1],2))+','+str(round(tr_data[k][2],2))+'n'
            
            try:
                sock.sendto(bytes(UDP_payload_PC[k], "utf-8"), PC_IPS[k])
                print("Message sent to PC IP: "+str(PC_IPS[k]))
            except:
                pass
    
    elif str(mode) == 'LISTENER':
        
        size_in = len(UDP_payload)
        
        if size_in == 1: 
        
            for k in range(size_in):
            
                UDP_payload[k] = '/'+str(int(tr_data[k][0]))+','+str(int(tr_data[k][1]))+'n'
                
                try:
                    sock.sendto(bytes(UDP_payload[k], "utf-8"), UDP_IPS[k][0])
                    print("Message sent to robot IP: "+str(UDP_IPS[k]))
                except:
                    pass
        else:
            print("LISTENER mode transmission is only available for one robot connection")
            sys.exit(0)
    
    else:
        print("Non-existent UDP transmission mode command")
        sys.exit(0)

def UDP_close():
    sock.close()

def initialize_seq(init_goal = seq_init_args.init_goal,
                   goal_file = seq_init_args.goal_file):
    
    with open(goal_file) as f:
        reader = csv.reader(f)
        lst = list(reader)
    
    globals()['sequence'] = lst
    globals()['start_time'] = time.time()
    globals()['prev_time'] = 0
    globals()['time_count'] = 0
    globals()['seq_goal'] = init_goal

    
def goal_seq_time():
    
    global sequence
    global start_time
    global prev_time
    global time_count
    global seq_goal
    
    current_time = time.time() - start_time
    abs_time = round(round(current_time, 1)-round(prev_time, 1), 1)
    prev_time = current_time
    
    if time_count < len(sequence):
    
        h, m, s, ds = sequence[time_count][0].split(':')
        time_k = round(float(h) * 3600 + float(m) * 60 + float(s) + float(ds)/10, 1)
        a = 0
        b = 3
        goal_total = []

        
        if abs_time != 0.0:
            
            if round(current_time, 1) == time_k:
                
                goal = sequence[time_count]
                del goal[0]
                goal = [int(x) for x in goal]
                
                number = int(len(goal)/3)
                
                for k in range (number):
                    k1 = goal[a:b]
                    goal_total.append(k1)
                    a = a + 3
                    b = b + 3
        
                time_count = time_count + 1
                seq_goal = goal_total
                
    return seq_goal
            
        
        
    
    