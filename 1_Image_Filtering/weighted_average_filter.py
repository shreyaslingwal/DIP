import numpy as np
from common import apply_kernel


def weighted_filter(img):
    k = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=float) / 16.0
    return apply_kernel(img, k)
