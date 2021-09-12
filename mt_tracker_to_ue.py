from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
import os
import socket
import struct
import datetime
import pyzed.sl as sl
import sys


class Worker(QObject):
    finished = pyqtSignal()
    running = True

    def run_Tracking(self):
        # Create a Camera object
        zed = sl.Camera()

        # Create a InitParameters object and set configuration parameters
        init_params = sl.InitParameters()
        init_params.camera_resolution = sl.RESOLUTION.HD720  # Use HD720 video mode (default fps: 60)
        # Use a right-handed Y-up coordinate system
        init_params.coordinate_system = sl.COORDINATE_SYSTEM.LEFT_HANDED_Z_UP
        init_params.coordinate_units = sl.UNIT.METER  # Set units in meters

        # Open the camera
        err = zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            exit(1)

        # Enable positional tracking with default parameters
        py_transform = sl.Transform()  # First create a Transform object for TrackingParameters object
        tracking_parameters = sl.PositionalTrackingParameters(_init_pos=py_transform)
        err = zed.enable_positional_tracking(tracking_parameters)
        if err != sl.ERROR_CODE.SUCCESS:
            exit(1)

        i = 0
        zed_pose = sl.Pose()

        zed_sensors = sl.SensorsData()
        runtime_parameters = sl.RuntimeParameters()

        position = [0, 0, 0, 0, 0, 0, 0]
        orientation = [0, 0, 0, 0]
        IP = "192.168.178.31"
        PORT = 9696

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        while self.running:
            if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
                # Get the pose of the left eye of the camera with reference to the world frame
                zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)
                zed.get_sensors_data(zed_sensors, sl.TIME_REFERENCE.IMAGE)
                zed_imu = zed_sensors.get_imu_data()

                # Display the translation and timestamp
                py_translation = sl.Translation()
                tx = round(zed_pose.get_translation(py_translation).get()[0], 3)
                ty = round(zed_pose.get_translation(py_translation).get()[1], 3)
                tz = round(zed_pose.get_translation(py_translation).get()[2], 3)
                # print("Translation: Tx: {0}, Ty: {1}, Tz {2}, Timestamp: {3}".format(tx, ty, tz, zed_pose.timestamp.get_milliseconds()), end="\r")

                # Display the orientation quaternion
                py_orientation = sl.Orientation()
                ox = round(zed_pose.get_orientation(py_orientation).get()[0], 3)
                oy = round(zed_pose.get_orientation(py_orientation).get()[1], 3)
                oz = round(zed_pose.get_orientation(py_orientation).get()[2], 3)
                ow = round(zed_pose.get_orientation(py_orientation).get()[3], 3)
                # print("Orientation: Ox: {0}, Oy: {1}, Oz {2}, Ow: {3}\n".format(ox, oy, oz, ow))

                position[0] = tx
                position[1] = ty
                position[2] = tz
                position[3] = ox
                position[4] = oy
                position[5] = oz
                position[6] = ow

                payload = struct.pack("7f", *position)
                sock.sendto(payload, (IP, PORT))
                print(struct.unpack("7f", payload), end="\r")
            else:
                print(zed.grab(runtime_parameters))
            i += 1

        # Close the camera and safe map
        area_file = "./area/" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".area"

        if not os.path.isdir("./area"):
            os.makedirs("./area", exist_ok=True)

        zed.save_area_map(area_file)

        zed.close()

        if os.path.isfile(area_file):
            print("Area file written: " + area_file)
        else:
            print("Area file could not be written")

        self.finished.emit()

    def change_state(self):
        print("Ending")
        if self.running:
            self.running = False
        else:
            self.running = True


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Camera tracker")
        self.resize(300, 300)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        # Button
        self.startBtn = QPushButton("Start", self)
        self.startBtn.clicked.connect(self.init_tracking)
        self.stopBtn = QPushButton("Stop", self)
        self.stopBtn.clicked.connect(self.)

        # Set Layout
        layout = QVBoxLayout()
        layout.addWidget(self.startBtn)
        layout.addWidget(self.stopBtn)
        self.centralWidget.setLayout(layout)

    def init_tracking(self):
        # Initialising threading
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        # Set up connections and clean threads afterwards
        self.thread.started.connect(self.worker.run_Tracking)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start thread
        self.thread.start()

        # Change button
        #self.startBtn.clicked.connect(self.worker.change_state)
        #self.startBtn.setText("Stop")
        #self.startBtn.cl

app = QApplication(sys.argv)
win = Window()
win.show()
app.exec()
#sys.exit(app.exec())