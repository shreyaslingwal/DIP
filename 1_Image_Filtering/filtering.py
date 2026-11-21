import os
import sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import rgb_to_hsi, hsi_to_rgb, make_sample_image
from mean_filter import mean_filter
from weighted_average_filter import weighted_filter
from gaussian_filter import gaussian_filter
from median_filter import median_filter
from laplacian_filter import laplacian_filter
from sobel_filter import sobel_filter
from prewitt_filter import prewitt_filter
from high_boost_filter import high_boost


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(base)
    in_path = os.path.join(root, "input", "input_image.png")
    out_dir = os.path.join(base, "outputs")
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(in_path):
        os.makedirs(os.path.dirname(in_path), exist_ok=True)
        make_sample_image(in_path)

    bgr = cv2.imread(in_path)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float64) / 255.0
    if max(rgb.shape[:2]) > 512:
        rgb = cv2.resize(rgb, (512, 512))

    hsi = rgb_to_hsi(rgb)
    H = hsi[:, :, 0]
    S = hsi[:, :, 1]
    I = hsi[:, :, 2]

    def save_rgb(name, new_I):
        new_hsi = np.dstack((H, S, np.clip(new_I, 0, 1)))
        out = (hsi_to_rgb(new_hsi) * 255).astype(np.uint8)
        cv2.imwrite(os.path.join(out_dir, name), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
        print(name)

    def save_gray(name, arr):
        cv2.imwrite(os.path.join(out_dir, name), (np.clip(arr, 0, 1) * 255).astype(np.uint8))
        print(name)

    save_rgb("0_original.png", I)
    cv2.imwrite(os.path.join(out_dir, "0_hsi_channels.png"),
                np.hstack([(H / 360 * 255).astype(np.uint8),
                           (S * 255).astype(np.uint8),
                           (I * 255).astype(np.uint8)]))

    save_rgb("1_mean_filter.png", mean_filter(I))
    save_rgb("2_weighted_average_filter.png", weighted_filter(I))
    save_rgb("3_gaussian_filter.png", gaussian_filter(I))
    save_rgb("4_median_filter.png", median_filter(I, 3))

    sharp, lap = laplacian_filter(I)
    save_rgb("5_laplacian_sharpened.png", sharp)
    save_gray("5b_laplacian_edge.png", np.abs(lap))

    sob, gx, gy = sobel_filter(I)
    save_gray("6_sobel_edge.png", sob)
    save_rgb("6b_sobel_on_intensity.png", sob)

    pre, gx2, gy2 = prewitt_filter(I)
    save_gray("7_prewitt_edge.png", pre)

    save_rgb("8_high_boost_A2.0.png", high_boost(I, 2.0))
    save_rgb("9_high_boost_A2.5.png", high_boost(I, 2.5))

    rng = np.random.default_rng(42)
    noisy = I.copy()
    mask = rng.random(I.shape)
    noisy[mask < 0.015] = 0
    noisy[(mask >= 0.015) & (mask < 0.03)] = 1.0
    save_rgb("10_noisy_salt_pepper.png", noisy)
    save_rgb("11_median_on_salt_pepper.png", median_filter(noisy, 3))

    noisy2 = np.clip(I + rng.normal(0, 0.08, I.shape), 0, 1)
    save_rgb("12_noisy_gaussian.png", noisy2)
    save_rgb("13_mean_on_gaussian_noise.png", mean_filter(noisy2))

    print("done")


if __name__ == "__main__":
    main()
