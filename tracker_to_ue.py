import pyzed.sl as sl
import socket, struct


def main():
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

    while True:
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

    # Close the camera
    zed.close()


if __name__ == "__main__":
    main()
