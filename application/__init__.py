from datetime import datetime
from flask import Flask
from flask.json import JSONEncoder

import os
import shutil
import mysql.connector

class MyJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return str(o)
        return o.__dict__

tmp_dir = "/tmp/floorplans"
app = Flask('fieldwire')
app.config["UPLOAD_FOLDER"] = tmp_dir
app.json_encoder = MyJsonEncoder
if os.path.exists(tmp_dir):
    shutil.rmtree(tmp_dir)
os.mkdir(tmp_dir)

sql_conn = mysql.connector.connect(user='fieldwire', password='password',
                              host='127.0.0.1',
                              database='fieldwire')

from application import projects, floorplans


@app.route('/')
def healthcheck():
    return 'OK', 200
