# Live Camera Tracking With ZED 2 For Unreal Engine

![ZED Navigator Web Interface](https://i.imgur.com/92KRVA0.jpg)

## Introduction
This repo provides a web application to use the Stereolabs ZED 2 camera for live camera tracking in Unreal Engine.
It was created during a university project and should be used with the customized Nvidia Jetson Nano from Hochschule der Medien for wireless tracking. 

## Dependencies
- CUDA capable GPU
- CUDA v11.0
- Stereolabs SDK v3.5.3
- Sterolabs Python "pyzed" module
- Python v3.8.8
- Python modules found in `python/requirements.txt`
- Unreal Engine v4.27
- Unreal Engine Plugin: [UDPCommunication](https://github.com/is-centre/udp-ue4-plugin-win64)

Newer versions of Python and Unreal Engine may be supported, but are not tested.

## Installation
Hochschule der Medien students please see the steps at the end of this file.

### Tracking device
1. Install all dependencies
2. Build the pyzed Python module

### Unreal Engine Workstation
1. Install the UDPCommunication plugin by copy & pasting the whole folder to `Unreal Projects\{your project}\Plugins`
2. Copy the `unreal/ZED_Cam.uasset` into your Unreal Engine content folder and restart Unreal Engine.

## How to track
Hochschule der Medien students please see the steps at the end of this file.

1. Plug in the ZED 2 camera
2. Start `CMD`:

    ```
    > cd path\to\camtrack
    > set FLASK_APP=server.py
    > python -m flask run
    ```
3. Navigate to the URL shown by flask to view the web interface
4. Set your IP address
5. Click on "Capture"
6. Start capturing
7. In Unreal Engine drag the ZED_Cam blueprint into your scene
8. Press `Alt + S`
9. The virtual camera should now react to movements

## Hochschule der Medien
You don't need to configure a tracking device, just use the Jetson Nano.

1. Plug the ZED Camera into the Jetson Nano
2. Start it up for about a minute
3. Connect to the "ZED NAVI" WIFI network
4. Visit the URL 1.1.1.1
5. Set your IP address
6. Click on "Capture"
7. Start capturing
8. In Unreal Engine drag the ZED_Cam blueprint into your scene
9. Press `Alt + S`
10. The virtual camera should now react to movements 

