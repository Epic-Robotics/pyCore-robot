import ucorobot

ucorobot.calibration(0, 0.05, "DICT_ARUCO_ORIGINAL", 9, 6, 0, None, 1280, 720)
"""
    Initialize the calibration process based on ArUco Markers.
    The calibration process uses the chessboard method.
    This function can use existing images or get new ones.
    
    Parameters
    ----------
    MODE : int
        Calibration mode. 0 --> Get new calibration images. 1 --> Use existing files
    MARKER_SIZE : float
        Length of one edge (in meters)
    DCT : str
        Predefined markers dictionaries/sets (default=DICT_ARUCO_ORIGINAL)
    BOARD_WIDTH : int
        Width of chessrboard's inner corners (default=9)
    BOARD_HEIGHT : int
        Height of chessboard's inner corners (default=6)
    CAM : int
        Camera source (default=0)
    API_CAM : str
        Camera capture API (default=None)
    WIDTH: int
        Width of camera resolution (default=640)
    HEIGHT : int
        Height of camera resolution (default=480)
"""