import numpy as np
import cv2
import glob
import os
import time
from .args import get_calib_args as calib_args

class ucoRobot:
    """
    A class for operations related to Aruco Markers.
    """
    
    def __get_images(self, cam, API_cam, board_width, board_height, width, height):
    
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
 
    def calibrate(self, mode = calib_args.mode, 
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
            self.__get_images(cam, API_cam, board_width, board_height, width, height)

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