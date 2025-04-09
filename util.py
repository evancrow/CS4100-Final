import math

from constants import HEX_SIZE, CENTER_X, CENTER_Y

def hex_to_pixel(q, r):
    x = HEX_SIZE * (math.sqrt(3) * q + (math.sqrt(3) / 2) * r)
    y = HEX_SIZE * (3 / 2 * r)

    return CENTER_X + x, CENTER_Y + y

def snap(px, py, digits=3):
    return round(px, digits), round(py, digits)