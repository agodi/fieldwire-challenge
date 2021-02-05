from flask import Flask

import os
import shutil

tmp_dir = "/tmp/floorplans"
app = Flask('fieldwire')
app.config["UPLOAD_FOLDER"] = tmp_dir
if os.path.exists(tmp_dir):
    shutil.rmtree(tmp_dir)
os.mkdir(tmp_dir)

from application import projects, floorplans


@app.route('/')
def healthcheck():
    return 'OK', 200