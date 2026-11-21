from mean_filter import mean_filter


def high_boost(img, A=2.0):
    blur = mean_filter(img)
    return A * img - blur
