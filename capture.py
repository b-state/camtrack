import socket
import struct
import os
import datetime
import time

import pyzed.sl as sl

fname = ""


# translate origin to center of cam
def transform_pose(zed_pose, tx):
    transform_ = sl.Transform()
    transform_.set_identity()
    # Translate the tracking frame by tx along the X axis
    transform_.m[0][3] = tx
    # Pose(new reference frame) = M.inverse() * pose (camera frame) * M, where M is the transform between the two frames
    transform_inv = sl.Transform()
    transform_inv.init_matrix(transform_)
    transform_inv.inverse()
    zed_pose = transform_inv * zed_pose * transform_


def main(toggle, ipaddress, save_map, file_name, load_file, latency_test):
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

    # Load area map if provided
    if load_file != None:
        tracking_parameters.area_file_path = load_file
        print("Area file used: ", load_file)

    err = zed.enable_positional_tracking(tracking_parameters)
    if err != sl.ERROR_CODE.SUCCESS:
        exit(1)

    zed_pose = sl.Pose()
    zed_sensors = sl.SensorsData()
    runtime_parameters = sl.RuntimeParameters()

    # initialise variables for udp
    position = [0] * 7
    ip = ipaddress
    port = 9696
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Get the distance between the center of the camera and the left eye
    translation_left_to_center = zed.get_camera_information().calibration_parameters.T[0]

    # Retrieve and transform the pose data into a new frame located at the center of the camera
    tracking_state = zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)
    transform_pose(zed_pose.pose_data(sl.Transform()), translation_left_to_center)

    # check if logging enabled
    if latency_test:
        print("latency test enabled")

    try:
        while toggle.value == 1:
            if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
                # Get the pose of the left eye of the camera with reference to the world frame
                zed.get_position(zed_pose, sl.REFERENCE_FRAME.WORLD)
                zed.get_sensors_data(zed_sensors, sl.TIME_REFERENCE.IMAGE)
                zed_imu = zed_sensors.get_imu_data()
                # Retrieve and transform the pose data into a new frame located at the center of the camera
                transform_pose(zed_pose.pose_data(sl.Transform()), translation_left_to_center)

                # Display the translation and timestamp
                py_translation = sl.Translation()
                tx = round(zed_pose.get_translation(py_translation).get()[0], 3)
                ty = round(zed_pose.get_translation(py_translation).get()[1], 3)
                tz = round(zed_pose.get_translation(py_translation).get()[2], 3)

                # Display the orientation quaternion
                py_orientation = sl.Orientation()
                ox = round(zed_pose.get_orientation(py_orientation).get()[0], 3)
                oy = round(zed_pose.get_orientation(py_orientation).get()[1], 3)
                oz = round(zed_pose.get_orientation(py_orientation).get()[2], 3)
                ow = round(zed_pose.get_orientation(py_orientation).get()[3], 3)

                # send timestamp for logging
                if latency_test:
                    data = time.time()
                    payload = struct.pack("1d", data)
                    sock.sendto(payload, (ip, port))

                else:
                    # assign translation and rotation and send via udp
                    position[0] = tx
                    position[1] = ty
                    position[2] = tz
                    position[3] = ox
                    position[4] = oy
                    position[5] = oz
                    position[6] = ow

                    payload = struct.pack("7f", *position)
                    sock.sendto(payload, (ip, port))
            else:
                print(zed.grab(runtime_parameters))

    except KeyboardInterrupt:
        pass

    # Close the camera and save map
    if save_map:
        print("File name:", file_name)

        # check if file name is set by user, if empty, set current time as file name
        # This should be rewritten, global variable not needed I guess
        if file_name == "":
            global fname
            fname = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
            print("Fname", fname)
        else:
            fname = file_name

        print("Name der Datei ist: " + fname)

        # construct file name
        area_file = "./area/" + fname + ".area"

        # check if area folder is exists, if not, make one
        if not os.path.isdir("./area"):
            os.makedirs("./area", exist_ok=True)

        # save map
        zed.save_area_map(area_file)

        zed.close()

        # check if area file has been written
        if os.path.isfile(area_file):
            print("Area file written: " + area_file)
        else:
            print("Area file could not be written")

    else:
        zed.close()


if __name__ == "__main__":
    main()
