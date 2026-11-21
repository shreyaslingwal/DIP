import numpy as np


def median_filter(img, size=3):
    p = size // 2
    padded = np.pad(img, p, mode="edge")
    parts = []
    for a in range(size):
        for b in range(size):
            parts.append(padded[a:a + img.shape[0], b:b + img.shape[1]])
    return np.median(np.dstack(parts), axis=2)
