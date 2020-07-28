import math
import numpy as np
import typing as tp

def vec2(x: tp.Tuple[float, float]) -> np.array:
    return np.array(x)

def unit(x: tp.Union[np.array, tp.Tuple[float, float]]) -> np.array:
    return x / np.linalg.norm(x)

def rad_to_deg(x: float) -> float:
    return x * 360 / (2*math.pi)

def deg_to_rad(x: float) -> float:
    return x * 2*math.pi / 360

def flip_y(coord: tp.Union[np.array, tp.Tuple[float, float]]) -> np.array:
    return np.array((coord[0], -coord[1]))

def get_angle_rad_between(a: tp.Union[np.array, tp.Tuple[float, float]], \
                          b: tp.Union[np.array, tp.Tuple[float, float]]) -> float:
    angle = math.acos( np.dot( unit(a), unit(b) ) )
    if angle > math.pi:
        angle = flip_angle(angle)
    return angle

def get_angle_deg_between(a: tp.Union[np.array, tp.Tuple[float, float]], \
                          b: tp.Union[np.array, tp.Tuple[float, float]]) -> float:
    return rad_to_deg( get_angle_rad_between(a,b) )

def get_bearing_rad_of(a: tp.Union[np.array, tp.Tuple[float, float]]) -> float:
    """Returns angle (radians) counter-clockwise to x-axis"""
    angle = math.acos( np.dot( unit(a), (1,0) ) )
    if a[1] < 0:
        angle = flip_angle(angle)
    return angle

def normalise_angle(rad: float) -> float:
    while rad > 2*math.pi:
        rad -= 2*math.pi

    while rad < 0:
        rad += 2*math.pi
    return rad

def flip_angle(rad: float) -> float:
    return 2*math.pi - rad

def get_unit_vector_after_rotating(start_vec: tp.Union[np.array, tp.Tuple[float, float]], \
                                   anti_clockwise_rad: float) -> np.array:
    new_angle_rad = get_bearing_rad_of( start_vec ) + anti_clockwise_rad
    ans_vec = (math.cos(new_angle_rad), math.sin(new_angle_rad))
    return unit(ans_vec)

def rotate_vector_right_angle(a: np.array) -> np.array:
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

def line_intersection(a1: np.array, a2: np.array, b1: np.array, b2: np.array) -> np.array:
    """
    Let line A be defined by endpoints a1, a2
    Let line B be defined by endpoints b1, b2
    Does not catch special cases like parallel lines or points
    """

    delta_a = a2-a1
    delta_b = b2-b1

    # Equation origin:
    # (a1 -> b1 -> intersection_point) dot A_perpendicular = 0
    # find intersection_point as "b1 + fraction of delta_b"
    delta_s = a1-b1
    delta_a_perp = rotate_vector_right_angle(delta_a)

    denom = np.dot( delta_a_perp, delta_b )
    num = np.dot( delta_a_perp, delta_s )
    return b1 + delta_b * (num/denom.astype(float))
