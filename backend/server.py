from flask import Flask, request
from places import *
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, support_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/")
def home():
    return "Hello World"

@app.route("/voronoi")
@cross_origin()
def voronoi():
    args = request.args
    print(args)
    print(float(args["long"]))
    print(float(args["lat"]))
    polygons = get_polygons(float(args["long"]), float(args["lat"]), args["search"])
    return polygons

if __name__ == "__main__":
    app.run()