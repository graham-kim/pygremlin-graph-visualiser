import math
import numpy
import typing as tp

def unit(x: tp.Tuple[float, float]) -> numpy.array:
    return x / numpy.linalg.norm(x)

def rad_to_deg(x: float) -> float:
    return x * 360 / (2*math.pi)

def deg_to_rad(x: float) -> float:
    return x * 2*math.pi / 360

def flip_y(coord: tp.Tuple[int, int]) -> tp.Tuple[int, int]:
    return (coord[0], -coord[1])

def get_unit_vector_after_rotating(start_vec: tp.Tuple[float, float], degrees: float):
    start_unit = unit(start_vec)
    start_angle_rad = math.acos( numpy.dot(start_unit, (1,0)) )
    if start_unit[1] < 0:
        start_angle_rad = 2*math.pi - start_angle_rad
    new_angle_rad = start_angle_rad + deg_to_rad(degrees)
    ans_vec = (math.cos(new_angle_rad), math.sin(new_angle_rad))
    return unit(ans_vec)
