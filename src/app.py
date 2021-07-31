from flask import Flask
import sys
from flask import jsonify
app = Flask(__name__)


@app.route("/")
def hello_world():
    return jsonify(sys.version_info)
