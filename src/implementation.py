import numpy as np
from typing import Tuple
import math
import utilities
import pandas as pd
import pyproj

def read_path_and_convert_to_gps(file_path: str) -> np.ndarray:
    """
    Read the path from the given file and return it as a numpy array.

    Parameters:
    file_path (str): Path to the file containing the path.

    Returns:
    np.ndarray: Numpy array containing the path.
    """
    # Read the file and extract the path
    path = np.loadtxt(file_path, delimiter=",", skiprows=1)
    path_gps = utilities.to_gps(path)
    pathGps = pd.DataFrame(path_gps, columns=["Latitude", "Longitude", "Altitude"])
    pathGps.to_csv("src\\data\\path_gps.csv", index=False)
    
    return path_gps

def convert_gps_to_utm(file_path: str) -> np.ndarray:
    """
    Convert GPS coordinates to UTM coordinates.
    Parameters:
    file_path (str): Path to the file containing the GPS coordinates.
    Returns:
    np.ndarray: Numpy array containing the UTM coordinates.
    """
    path_gps = pd.read_csv(file_path)
    lats, lons, alts = path_gps["Latitude"], path_gps["Longitude"], path_gps["Altitude"]
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32612", always_xy=True)
    utm_coords =  np.array([transformer.transform(lon, lat, alt) for lon, lat, alt in zip(lons, lats, alts)])
    utm_coords_save = pd.DataFrame(utm_coords, columns=["Easting", "Northing", "Altitude"])
    # Save the UTM coordinates to a CSV file
    utm_coords_save.to_csv("src\\data\\path_utm.csv", index=False)

    return utm_coords


def compute_closest_point(path: np.ndarray, point: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute the closest point on the path to the given point.

    Parameters:
    path (np.ndarray): Numpy array containing the path.
    point (np.ndarray): Numpy array containing the point.

    Returns:
    np.ndarray: Numpy array containing the closest point on the path.
    """
    distances = np.linalg.norm(path - point, axis=1)
    closest_index = np.argmin(distances)

    if closest_index < len(path) - 1:
        return path[closest_index], path[closest_index+np.int64(1)]
    else:
        return path[closest_index-1], path[closest_index]
        
def compute_path_vector(point1: np.ndarray, point2: np.ndarray) -> np.ndarray:
    """
    Computes the vector on the path, with the reference point as the closest point to the rover
    
    Parameters:
    point (np.ndarray): Numpy array containing the point.
    
    Returns:
    np.ndarray: Numpy array containing the vector on the path.
    """
    vector = point2 - point1
    return vector
    
def calculate_angle(dirvector1: np.ndarray, dirvector2: np.ndarray) -> float:
    """
    Calculate the angle between the given two numpy vectors. This will be helpful for putting the robot back on to the path.

    Parameters:
    vector1 (np.ndarray): First input vector.
    vector2 (np.ndarray): Second input vector.

    Returns:
    float: Angle in radians between the two vectors.
    """
    # Normalize the input vectors
    norm_vector1 = dirvector1 / np.linalg.norm(dirvector1)
    norm_vector2 = dirvector2 / np.linalg.norm(dirvector2)
    
    # Calculate the dot product
    dot_product = np.dot(norm_vector1, norm_vector2)
    dot_product = np.clip(dot_product, -1.0, 1.0)  # Ensure the value is within the valid range for arccos
    
    # Calculate the angle in radians
    angle = np.arccos(dot_product)
    angle_deg = np.degrees(angle)
    if(angle_deg > 180):
        angle_deg = 360 - angle_deg
    return angle_deg


def main():
    # Read the path from the file
    path = read_path_and_convert_to_gps("src\\data\\path.csv")
    path_utm = convert_gps_to_utm("src\\data\\path_gps.csv")
    rover_heading = 10 # Facing value degrees counterclockwise from North
    rover_unit_vector = np.array([np.cos(np.radians(rover_heading)), np.sin(np.radians(rover_heading)), 0]) # This is the unit vector of the rover heading
    # Compute the closest point on the path to the given point
    # point_EPSG = np.array([5.1852832e+05, 4.2530578e+06, 1.36997e+03])
    rover_point_GPS = np.array([38.41304679127861, -110.78761974198939, 1362.1]) #theoretical rover point
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32612", always_xy=True)
    rover_point_UTM = np.array(transformer.transform(rover_point_GPS[1], rover_point_GPS[0], rover_point_GPS[2]))
    map_reflection, head_point = compute_closest_point(path_utm, rover_point_UTM)
    print(rover_point_UTM, head_point, map_reflection)
    path_vector = compute_path_vector(map_reflection, head_point) # This is the vector from map reflection to the head point
    rover_path_vector = compute_path_vector(rover_point_UTM, head_point) #This is the vector which rover must face
    print(rover_path_vector)
    # Calculate the angle between two vectors
    angle = calculate_angle(rover_path_vector, rover_unit_vector)
    # The rover will turn by the above angle to get back on the path heading, and then will have to move a certain distance forward unti it is on the path.
    
    distance_to_move = np.linalg.norm(rover_path_vector)
    print(distance_to_move)
    print(angle)


if __name__ == "__main__":
    main()