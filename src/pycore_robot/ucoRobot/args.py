import argparse

Uco = argparse.ArgumentParser("Uco Robots library parameters")
subparsers = Uco.add_subparsers(help='Command help for Uco Robots library')

def get_calib_args():
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

    return calib.parse_args()