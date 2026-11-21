import numpy as np
from common import apply_kernel


def prewitt_filter(img):
    kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=float)
    ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=float)
    gx = apply_kernel(img, kx)
    gy = apply_kernel(img, ky)
    mag = np.sqrt(gx ** 2 + gy ** 2)
    return mag, gx, gy
