from flask import Flask
from flask import jsonify

from matching import get_all_interns

app = Flask(__name__)
app.debug= True
@app.route("/")
def hello_world():
    return "<p>Hellooo World!</p>"

@app.route("/api")
def me_api():
    interns = get_all_interns()
    print(interns)
    return jsonify([intern for intern in interns])