import numpy as np
import math

def rotation(phi, axis='x'):
    radian_angle = phi / 180 * math.pi
    phi_sine = math.sin(radian_angle)
    phi_cosine = math.cos(radian_angle)
    if axis == 'x':
        return np.array([[1, 0, 0, 0],
                         [0, phi_cosine, -phi_sine, 0],
                         [0, phi_sine, phi_cosine, 0],
                         [0, 0, 0, 1]])
    elif axis == 'y':
        return np.array([[phi_cosine, 0, phi_sine, 0],
                         [0, 1, 0, 0],
                         [-phi_sine, 0, phi_cosine, 0],
                         [0, 0, 0, 1]])
    elif axis == 'z':
        return np.array([[phi_cosine, -phi_sine, 0, 0],
                         [phi_sine, phi_cosine, 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]])
    else:
        return np.identity(4)
    
def translation(x, y, z):
    return np.array([[1, 0, 0, x],
                     [0, 1, 0, y],
                     [0, 0, 1, z],
                     [0, 0, 0, 1]])
                     
def scale(x, y, z):
    return np.array([[x, 0, 0, 0],
                     [0, y, 0, 0],
                     [0, 0, z, 0],
                     [0, 0, 0, 1]])
                     
def extract_location(frame):
    return np.array([frame[0][3], frame[1][3], frame[2][3]])