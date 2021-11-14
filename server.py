from multiprocessing import Process, Value

from flask import Flask, request, render_template

from capture import main as only_capture

from capture_and_safe import main as cands

app = Flask(__name__)

toggle = Value("i", 1)

ipaddress = "0.0.0.0"

def zed_capture():
    global toggle
    toggle.value = 1
    p = Process(target=only_capture, args=(toggle, ipaddress), name="ZED Capture")
    p.start()
    print("Tracking should have started")
    pass

def zed_capture_and_safe(fname):
    global toggle
    toggle.value = 1
    p = Process(target=cands, args=(toggle, fname), name="ZED Capture And Safe")
    p.start()
    print("Tracking should have started")
    pass


def zed_stop():
    global toggle
    toggle.value = 0


@app.route("/", methods=['GET', 'POST'])
def index():
    global ipaddress

    if request.form.get("set_ip") == "SET IP":
        ipaddress = request.form.get("ipaddress")

    print("Address is:",ipaddress)


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

    fname = request.form.get("fname")

    if request.form.get("toggle") == "start":
        print(fname)
        zed_capture_and_safe(fname)
    if request.form.get("toggle") == "stop":
        zed_stop()

    return render_template("capture_and_safe.html", fname=fname)
