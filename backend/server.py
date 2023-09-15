from flask import Flask, request
from places import *
from flask_cors import CORS, cross_origin
import time

if __name__ == "__main__":
    app = Flask(__name__)
    CORS(app)
    time.sleep(1)
    @app.route("/")
    def home():
        return "Hello World"

    @app.route("/Geovor/v1/voronoi")
    @cross_origin(origin='*')
    def voronoi():
        args = request.args
        print(args)
        print(float(args["long"]))
        print(float(args["lat"]))
        polygons = get_polygons(float(args["long"]), float(args["lat"]), args["search"])
        return polygons
    app.run()