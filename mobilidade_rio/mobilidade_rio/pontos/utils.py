import geopy.distance


def get_distance(p1: tuple, p2: tuple) -> float:
    return geopy.distance.great_circle(p1, p2).meters


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default
