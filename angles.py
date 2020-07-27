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
