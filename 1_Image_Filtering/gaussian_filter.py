import numpy as np
from common import apply_kernel


def gaussian_kernel(size, sigma):
    ax = np.arange(size) - size // 2
    xx, yy = np.meshgrid(ax, ax)
    k = np.exp(-(xx ** 2 + yy ** 2) / (2 * sigma ** 2))
    return k / k.sum()


def gaussian_filter(img):
    return apply_kernel(img, gaussian_kernel(5, 1.0))
