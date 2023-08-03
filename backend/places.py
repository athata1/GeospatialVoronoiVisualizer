import requests
import os
from dotenv import load_dotenv
import numpy as np

import matplotlib.pyplot as plt
from scipy.ndimage import binary_erosion
from scipy.spatial import Voronoi
from shapely.geometry import Point, Polygon, GeometryCollection
from skimage import draw
from sklearn.neighbors import KDTree
import math

load_dotenv()

url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
radius = 10000

def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstruct infinite voronoi regions in a 2D diagram to finite
    regions.

    Parameters
    ----------
    vor : Voronoi
        Input diagram
    radius : float, optional
        Distance to 'points at infinity'.

    Returns
    -------
    regions : list of tuples
        Indices of vertices in each revised Voronoi regions.
    vertices : list of tuples
        Coordinates for revised Voronoi vertices. Same as coordinates
        of input vertices, with 'points at infinity' appended to the
        end.

    """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1] # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)

def get_circular_se(radius=2):

    N = (radius * 2) + 1
    se = np.zeros(shape=[N,N])
    for i in range(N):
        for j in range(N):
                se[i,j] = (i - N / 2)**2 + (j - N / 2)**2 <= radius**2
    se = np.array(se, dtype="uint8")
    return se

def polygonize_by_nearest_neighbor(pp):
    """Takes a set of xy coordinates pp Numpy array(n,2) and reorders the array to make
    a polygon using a nearest neighbor approach.

    """

    # start with first index
    pp_new = np.zeros_like(pp)
    pp_new[0] = pp[0]
    p_current_idx = 0

    tree = KDTree(pp)

    for i in range(len(pp) - 1):

        nearest_dist, nearest_idx = tree.query([pp[p_current_idx]], k=4)  # k1 = identity
        nearest_idx = nearest_idx[0]

        # finds next nearest point along the contour and adds it
        for min_idx in nearest_idx[1:]:  # skip the first point (will be zero for same pixel)
            if not pp[min_idx].tolist() in pp_new.tolist():  # make sure it's not already in the list
                pp_new[i + 1] = pp[min_idx]
                p_current_idx = min_idx
                break

    pp_new[-1] = pp[0]
    return pp_new

def get_data(long, lat, search):
    key = os.getenv('API_KEY')
    data = requests.get(f'{url}?keyword={search}&location={long}%2C{lat}&radius={radius}&key={key}&rankby=prominence')
    #print(data.json()['results'])
    return data


def get_location_data(long, lat, search):
    
    coordinates = []
    
    data = get_data(long, lat, search)

    json = data.json()
    for location in json['results']:
        coords = []
        long_lat = location['geometry']['location']
        coords.append(long_lat['lat'])
        coords.append(long_lat['lng'])
        coords.append(location['name'])
        coordinates.append(coords)
    return np.array(coordinates)

def get_polygons(long, lat, search):
    location_data = get_location_data(long, lat, search)
    #create copy of original data points
    orig_points = np.copy(location_data).tolist()
    
    points = np.delete(location_data, 2, 1)
    points = np.array(points, dtype='float64')
    
    points[:,0] += 300
    points[:,1] += 300

    vor = Voronoi(points)
    
    min_x = vor.min_bound[0] - 0.1
    max_x = vor.max_bound[0] + 0.1
    min_y = vor.min_bound[1] - 0.1
    max_y = vor.max_bound[1] + 0.1
    
    regions, vertices = voronoi_finite_polygons_2d(vor)
    '''print("--")
    print(regions)
    print("--")
    print(vertices)'''
    box = Polygon([[min_x, min_y], [min_x, max_y], [max_x, max_y], [max_x, min_y]])

    mean_x = np.mean(points[:, 0])
    mean_y = np.mean(points[:, 1])
    rad = 0
    delta = 0.04
    for point in points:
        rad = max(math.sqrt((mean_x - point[0] + delta)**2 + (mean_y - point[1] + delta)**2), rad)

    circle = Point(mean_x, mean_y).buffer(rad)
    print(list(circle.exterior.coords))

    # colorize
    out_coords = []
    for region in regions:
        poly_reg = vertices[region]
        shape = list(poly_reg.shape)
        shape[0] += 1
        p:Polygon = Polygon(np.append(poly_reg, poly_reg[0]).reshape(*shape)).intersection(circle)
        if (type(p) == GeometryCollection):
                p = p.geoms[0]
        poly = (np.array(p.exterior.coords)).tolist()
        coords = np.array(p.exterior.coords)
        coords[:,0] -= 300
        coords[:, 1] -= 300
        out_coords.append(coords.tolist())
        if __name__ == "__main__":
            plt.fill(*zip(*poly), alpha=0.4)
    
    
    if __name__ == "__main__":
        plt.plot(points[:,0], points[:,1], 'ko', ms=2)
        plt.xlim(vor.min_bound[0] - 0.1, vor.max_bound[0] + 0.1)
        plt.ylim(vor.min_bound[1] - 0.1, vor.max_bound[1] + 0.1)

        plt.show()
    return [out_coords, orig_points]
    

'''def get_polygons(long, lat, search):
    location_data = get_location_data(long, lat, search)
    #create copy of original data points
    orig_points = np.copy(location_data).tolist()
    
    points = np.delete(location_data, 2, 1)
    points = np.array(points, dtype='float64')

    points[:,0] += 300
    points[:,1] += 300

    min_x = points.min(axis=0)[0]
    min_y = points.min(axis=0)[1]
    max_x = points.max(axis=0)[0]
    max_y = points.max(axis=0)[1]
    mean_x = np.mean(points[:, 0])
    mean_y = np.mean(points[:, 1])
    
    rad = 0
    for point in points:
        rad = max(math.sqrt((mean_x - point[0])**2 + (mean_y - point[1])**2) + 20, rad)


    #generates a circular mask
    side_len = int(rad*2+100)
    mask = np.zeros(shape=(side_len, side_len))
    rr, cc = draw.circle_perimeter(int(mean_y), int(mean_x), radius=int(rad), shape=mask.shape)
    mask[rr, cc] = 1
    fig, ax = plt.subplots()
    ax.imshow(mask,cmap='Greys_r')
    ax.plot(points[:,0],points[:,1],'ro',ms=2)
    plt.show()

    #makes a polygon from the mask perimeter
    se = get_circular_se(radius=1)
    contour = mask - binary_erosion(mask, structure=se)
    pixels_mask = np.array(np.where(contour==1)[::-1]).T
    polygon = polygonize_by_nearest_neighbor(pixels_mask)
    polygon = Polygon(polygon)

    # returns a list of the centroids that are contained within the polygon
    new_points = []
    for point in points:
        if polygon.contains(Point(point)):
            new_points.append(point)

    #performs voronoi tesselation
    if len(points) > 3: #otherwise the tesselation won't work
        vor = Voronoi(new_points)
        regions, vertices = voronoi_finite_polygons_2d(vor)

        #clips tesselation to the mask
        new_vertices = []
        out_coords = []
        for region in regions:
            poly_reg = vertices[region]
            shape = list(poly_reg.shape)
            shape[0] += 1
            p:Polygon = Polygon(np.append(poly_reg, poly_reg[0]).reshape(*shape)).intersection(polygon)
            if (type(p) == GeometryCollection):
                p = p.geoms[0]
            coords = np.array(p.exterior.coords)
            coords[:,0] -= 300
            coords[:, 1] -= 300
            out_coords.append(coords.tolist())
            poly = (np.array(p.exterior.coords)).tolist()
            new_vertices.append(coords.tolist())
        
        if __name__ == "__main__":
            #plots the results
            fig, ax = plt.subplots()
            #ax.imshow(mask,cmap='Greys_r')
            for poly in new_vertices:
                ax.fill(*zip(*poly), alpha=0.7, color=(np.random.uniform(0, 1),np.random.uniform(0, 1),np.random.uniform(0, 1)))
            ax.plot(points[:,0] - 300,points[:,1] - 300,'ro',ms=2)
            plt.show()
        return [out_coords, orig_points]
'''
if __name__ == "__main__":
    #get_polygons(40.7128,-74.0060,'starbucks')
    print(get_polygons(40.7128,-74.0060,'dunkin'))