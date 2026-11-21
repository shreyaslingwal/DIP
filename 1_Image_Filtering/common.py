import numpy as np
import cv2


def rgb_to_hsi(rgb):
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]

    I = (r + g + b) / 3.0
    mn = np.minimum(np.minimum(r, g), b)
    S = 1 - mn / np.maximum(I, 1e-10)
    S = np.where(I == 0, 0, S)

    num = 0.5 * ((r - g) + (r - b))
    den = np.sqrt((r - g) ** 2 + (r - b) * (g - b)) + 1e-10
    theta = np.degrees(np.arccos(np.clip(num / den, -1, 1)))
    H = np.where(b <= g, theta, 360 - theta)
    H = np.where(S == 0, 0, H)

    return np.dstack((H, S, I))


def hsi_to_rgb(hsi):
    H = hsi[:, :, 0]
    S = hsi[:, :, 1]
    I = hsi[:, :, 2]
    out = np.zeros_like(hsi)

    m1 = (H >= 0) & (H < 120)
    m2 = (H >= 120) & (H < 240)
    m3 = (H >= 240) & (H <= 360)

    for mask, start in [(m1, 0), (m2, 120), (m3, 240)]:
        h = np.radians(H - start)
        cos_val = np.cos(h) / np.maximum(np.cos(np.radians(60) - h), 1e-10)
        if start == 0:
            bb = I * (1 - S)
            rr = I * (1 + S * cos_val)
            gg = 3 * I - rr - bb
        elif start == 120:
            rr = I * (1 - S)
            gg = I * (1 + S * cos_val)
            bb = 3 * I - rr - gg
        else:
            gg = I * (1 - S)
            bb = I * (1 + S * cos_val)
            rr = 3 * I - gg - bb
        out[:, :, 0] = np.where(mask, rr, out[:, :, 0])
        out[:, :, 1] = np.where(mask, gg, out[:, :, 1])
        out[:, :, 2] = np.where(mask, bb, out[:, :, 2])

    return np.clip(out, 0, 1)


def apply_kernel(img, kernel):
    kh = kernel.shape[0]
    kw = kernel.shape[1]
    pad_h = kh // 2
    pad_w = kw // 2
    padded = np.pad(img, ((pad_h, pad_h), (pad_w, pad_w)), mode="edge")
    k = np.flip(kernel)
    res = np.zeros_like(img, dtype=np.float64)
    for a in range(kh):
        for b in range(kw):
            res += k[a, b] * padded[a:a + img.shape[0], b:b + img.shape[1]]
    return res


def make_sample_image(path, size=512):
    img = np.zeros((size, size, 3), dtype=np.uint8)
    for y in range(size):
        for x in range(size):
            img[y, x] = [int(255 * x / size), int(255 * y / size), 128]
    cv2.circle(img, (140, 140), 80, (0, 0, 255), -1)
    cv2.circle(img, (380, 130), 65, (0, 255, 0), -1)
    cv2.rectangle(img, (60, 300), (230, 450), (255, 0, 0), -1)
    cv2.rectangle(img, (290, 290), (460, 460), (0, 255, 255), -1)
    for i in range(0, size, 32):
        cv2.line(img, (i, 0), (i, size), (30, 30, 30), 1)
        cv2.line(img, (0, i), (size, i), (30, 30, 30), 1)
    cv2.imwrite(path, img)
    return img
