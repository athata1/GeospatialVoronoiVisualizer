import requests
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
radius = 1500
def get_data(long, lat, search):
    key = os.getenv('API_KEY')
    data = requests.get(f'{url}?keyword={search}&location={long}%2C{lat}&radius={radius}&key={key}')
    return data


def get_location_data():
    
    coordinates = []
    
    data = get_data(40.7128,-74.0060,'gym')
    #print(data.text)

    json = data.json()
    for location in json['results']:
        coords = []
        long_lat = location['geometry']['location']
        coords.append(long_lat['lat'])
        coords.append(long_lat['lng'])
        coords.append(location['name'])
        coordinates.append(coords)
    return np.array(coordinates)
        
location_data = get_location_data()
coordinates = np.delete(location_data, 2, 1)
print(location_data)