import git
import os
import time
from multiprocessing import Process, Value
from flask import Flask, request, render_template
from capture import main as only_capture

app = Flask(__name__)

toggle = Value("i", 1)

ipaddress = "0.0.0.0"

safe_map = False
load_map = False

fname = None

project_path = os.path.dirname(os.path.realpath(__file__))


def zed_capture():
    global toggle
    toggle.value = 1
    p = Process(target=only_capture, args=(toggle, ipaddress, safe_map, fname), name="ZED Capture")
    p.start()
    print("Tracking should have started")
    pass


def zed_stop():
    global toggle
    toggle.value = 0

def get_dict_filenames(path):
    for dirpath, dirnames, file_names in os.walk(path):
        return file_names


@app.route("/", methods=['GET', 'POST'])
def index():
    global ipaddress

    if request.form.get("set_ip") == "SET IP":
        ipaddress = request.form.get("ipaddress")

    print("Address is:", ipaddress)

    return render_template("index.html", ipaddress=ipaddress)


@app.route("/capture", methods=['GET', 'POST'])
def capture():
    if request.form.get("toggle") == "start":
        zed_capture()
    if request.form.get("toggle") == "stop":
        zed_stop()

    return render_template("capture.html")


@app.route("/capture_and_safe", methods=['GET', 'POST'])
def capture_and_safe():
    global fname
    global safe_map
    fname = request.form.get("fname")

    safe_map = True

    if request.form.get("toggle") == "start":
        print(fname)
        zed_capture()
    if request.form.get("toggle") == "stop":
        zed_stop()
        safe_map = False

    return render_template("capture_and_safe.html", fname=fname)


@app.route("/load_and_capture", methods=['GET', 'POST'])
def load_and_capture():

    filenames = get_dict_filenames(os.path.join(project_path, "area"))

    print(request.form.get("selection"))

    return render_template("load_and_capture.html", filenames=filenames)


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    if request.form.get("action") == "restart":
        os.system('sudo restart')
    if request.form.get("action") == "shutdown":
        os.system('sudo poweroff')
    if request.form.get("action") == "update":
        repo = git.Repo("/home/nano/camtrack/")
        repo.remotes.origin.pull()
        time.sleep(10)
        os.system('sudo restart')
    return render_template("settings.html")
