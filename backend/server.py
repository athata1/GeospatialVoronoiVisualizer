from flask import Flask, request
from places import *

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello World"

@app.route("/voronoi")
def voronoi():
    args = request.args
    #return args
    print(float(args["long"]))
    polygons = get_polygons(float(args["long"]), float(args["lat"]), args["search"])
    return polygons

if __name__ == "__main__":
    app.run()