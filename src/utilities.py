import numpy as np
from geopy import distance
from pyproj import Transformer

GPS_CRS="EPSG:4326"
POINT_CRS="EPSG:32612"

def dist_gps(point_1: tuple[float], point_2: tuple[float]) -> float:
    """
    Calculate the distance between two points in GPS coordinates using the geopy library.

    Args:
        point_1 - first point represented as a tuple (latitude, longitude)
        point_2 - second point represented as a tuple (latitude, longitude)

    Returns:
        Distance in meters between the two points.
    """
    return distance.distance(point_1[:2], point_2[:2]).m

def getcsv(pdal_json: str):
    """
    Reads json and gets the csv file from the 
    """

"""
Converts points in the (x, y, z) format from laz format to GPS format

Args:
    points - numpy array of dimension (n x 3) with each row being a tuple of lat,
             lon, alt
    source_crs - source coordinate reference system for the points
Returns:
    List of points in the format (n x 3) where each point is now referencing GPS
    reference system
"""
def to_gps(points: np.ndarray, source_crs=POINT_CRS) -> np.ndarray:
    transformer = Transformer.from_crs(source_crs, GPS_CRS, always_xy=True)
    result = np.array([transformer.transform(x, y, z) for x, y, z in points])
    result[:, [0, 1]] = result[:, [1, 0]]
    return result

