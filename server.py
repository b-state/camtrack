from multiprocessing import Process, Value

from flask import Flask, request, render_template

from capture import main as only_capture

from capture_and_safe import main as cands

app = Flask(__name__)

toggle = Value("i", 1)

def zed_capture():
    global toggle
    toggle.value = 1
    p = Process(target=only_capture, args=(toggle,))
    p.start()
    print("Tracking should have started")
    pass

def zed_capture_and_safe(fname):
    global toggle
    toggle.value = 1
    p = Process(target=cands, args=(toggle, fname))
    p.start()
    print("Tracking should have started")
    pass


def zed_stop():
    global toggle
    toggle.value = 0


@app.route("/")
def index():
    return render_template("index.html")


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
