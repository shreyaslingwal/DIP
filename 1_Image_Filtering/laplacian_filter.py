import numpy as np
from common import apply_kernel


def laplacian_filter(img):
    k = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=float)
    lap = apply_kernel(img, k)
    sharp = img - lap
    return sharp, lap
