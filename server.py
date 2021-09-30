from flask import Flask, request, render_template
from capture import main
from multiprocessing import Process
from test import test

app = Flask(__name__)

def zed_capture():
    p = Process(target=main())
    p.start()
    print("Test")
    pass

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/capture", methods=['GET', 'POST'])
def capture():

    if request.form.get("toggle") == "start":
        zed_capture()

    return render_template("capture.html")