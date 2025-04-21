from geopy import distance

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