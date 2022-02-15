import os
import subprocess
from multiprocessing import Process, Value

from flask import Flask, request, render_template, send_from_directory

from capture import main as only_capture

app = Flask(__name__)

# Initialise variables for functions.
# Global variables everywhere!!! Beginner project, pls don't judge :/
# toggle: is used to start tracking on a new processor.
# ipaddress: destination where udp packeges should be sent
# save_map: bool for creating an .area file or not
# load_map: bool for loading an .area file or not
# fname: file name for .area file given by user, if not set it will be "None"
# selection: file name of area file choosen by user to be used for tracking
# latency_test: bool if should be in latency mode or tracking mode
# project_path: get project directory. Used for loading saved .area files

toggle = Value("i", 1)
ipaddress = "0.0.0.0"
save_map = False
load_map = False
load_file = None
fname = None
selection = None
latency_test = False
project_path = os.path.dirname(os.path.realpath(__file__))


# The general procedure is that the methods get their values through a post request,
# check the answer of the request and set variables accordingly

# start capturing with previous set variables
def zed_capture():
    global toggle
    toggle.value = 1
    p = Process(target=only_capture, args=(toggle, ipaddress, save_map, fname, load_file, latency_test),
                name="ZED Capture")
    p.start()
    print("Tracking should have started")
    pass


# stop tracking
def zed_stop():
    global toggle
    toggle.value = 0


# get file names for area map loading
def get_dict_filenames(path):
    for dirpath, dirnames, file_names in os.walk(path):
        return file_names


# favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# start page, ip address of destination is required
@app.route("/", methods=['GET', 'POST'])
def index():
    global ipaddress

    if request.form.get("set_ip") == "SET IP":
        ipaddress = request.form.get("ipaddress")

    print("Address is:", ipaddress)

    return render_template("index.html", ipaddress=ipaddress)


# normal capture mode
@app.route("/capture", methods=['GET', 'POST'])
def capture():
    if request.form.get("toggle") == "start":
        zed_capture()

    if request.form.get("toggle") == "stop":
        zed_stop()

    return render_template("capture.html")


# capture and save map mode
@app.route("/capture_and_save", methods=['GET', 'POST'])
def capture_and_save():
    global fname
    global save_map
    fname = request.form.get("fname")

    save_map = True

    if request.form.get("toggle") == "start":
        print(fname)
        zed_capture()

    if request.form.get("toggle") == "stop":
        zed_stop()
        save_map = False

    return render_template("capture_and_save.html", fname=fname)


# load a .area file and use it for tracking
@app.route("/load_and_capture", methods=['GET', 'POST'])
def load_and_capture():
    global selection
    global load_file

    filenames = get_dict_filenames(os.path.join(project_path, "area"))
    selection = request.form.get("selection")

    if request.form.get("toggle") == "start":
        load_file = selection
        zed_capture()

    if request.form.get("toggle") == "stop":
        zed_stop()

    return render_template("load_and_capture.html", filenames=filenames, selection=selection)


# settings menu
@app.route("/settings", methods=['GET', 'POST'])
def settings():
    global latency_test

    if request.form.get("toggle") == "restart":
        subprocess.call(["bash", "reboot"])

    if request.form.get("toggle") == "shutdown":
        subprocess.call(["bash", "poweroff"])

    if request.form.get("toggle") == "latency_test":
        latency_test = True
        zed_capture()

    if request.form.get("toggle") == "latency_test_stop":
        latency_test = False
        zed_stop()

    return render_template("settings.html")
