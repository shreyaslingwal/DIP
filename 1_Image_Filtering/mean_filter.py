import numpy as np
from common import apply_kernel


def mean_filter(img):
    k = np.ones((3, 3)) / 9.0
    return apply_kernel(img, k)
