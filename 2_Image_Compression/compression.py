import os
import sys
import json
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from huffman import huffman_compress, huffman_decompress
from arithmetic import arithmetic_compress, arithmetic_decompress


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(base)
    in_path = os.path.join(root, "input", "input_image.png")
    out_dir = os.path.join(base, "outputs")
    os.makedirs(out_dir, exist_ok=True)

    if not os.path.exists(in_path):
        sys.path.insert(0, os.path.join(root, "1_Image_Filtering"))
        from common import make_sample_image
        os.makedirs(os.path.dirname(in_path), exist_ok=True)
        make_sample_image(in_path)

    img = cv2.imread(in_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (256, 256))
    data = gray.tobytes()
    n = gray.size
    orig_size = len(data)

    cv2.imwrite(os.path.join(out_dir, "0_original_gray.png"), gray)

    results = {}
    results["image_shape"] = list(gray.shape)
    results["original_size_bytes"] = orig_size

    packed, info = huffman_compress(data)
    f = open(os.path.join(out_dir, "huffman_compressed.bin"), "wb")
    f.write(packed)
    f.close()

    decoded = huffman_decompress(packed, info)
    recon = np.frombuffer(decoded, dtype=np.uint8).reshape(gray.shape)
    cv2.imwrite(os.path.join(out_dir, "1_huffman_reconstructed.png"), recon)

    huff = {}
    huff["original_size_bytes"] = orig_size
    huff["compressed_size_bytes"] = len(packed)
    huff["compression_ratio"] = round(orig_size / len(packed), 4)
    huff["space_saving_percent"] = round((1 - len(packed) / orig_size) * 100, 2)
    huff["bits_per_pixel"] = round(info["total_bits"] / n, 4)
    huff["entropy_bits_per_symbol"] = round(info["entropy"], 4)
    huff["avg_code_length"] = round(info["avg_code_length"], 4)
    huff["unique_symbols"] = len(info["codes"])
    huff["lossless"] = bool(np.array_equal(gray, recon))
    sample = {}
    for k in sorted(info["codes"])[:10]:
        sample[str(k)] = info["codes"][k]
    huff["sample_codes"] = sample
    results["huffman"] = huff
    print("huffman:", huff)

    packed2, info2 = arithmetic_compress(data)
    f = open(os.path.join(out_dir, "arithmetic_compressed.bin"), "wb")
    f.write(packed2)
    f.close()

    decoded2 = arithmetic_decompress(packed2, info2)
    recon2 = np.frombuffer(decoded2, dtype=np.uint8).reshape(gray.shape)
    cv2.imwrite(os.path.join(out_dir, "2_arithmetic_reconstructed.png"), recon2)

    arith = {}
    arith["original_size_bytes"] = orig_size
    arith["compressed_size_bytes"] = len(packed2)
    arith["compression_ratio"] = round(orig_size / len(packed2), 4)
    arith["space_saving_percent"] = round((1 - len(packed2) / orig_size) * 100, 2)
    arith["bits_per_pixel"] = round(info2["total_bits"] / n, 4)
    arith["unique_symbols"] = len(info2["frequencies"])
    arith["lossless"] = bool(np.array_equal(gray, recon2))
    results["arithmetic"] = arith
    print("arithmetic:", arith)

    f = open(os.path.join(out_dir, "compression_results.json"), "w")
    json.dump(results, f, indent=2)
    f.close()

    f = open(os.path.join(out_dir, "compression_results.txt"), "w")
    f.write("image compression results\n")
    f.write("image: %dx%d gray, %d pixels\n" % (gray.shape[1], gray.shape[0], n))
    f.write("original size: %d bytes\n\n" % orig_size)
    for name in ["huffman", "arithmetic"]:
        f.write(name + "\n")
        for k, v in results[name].items():
            f.write("%s: %s\n" % (k, v))
        f.write("\n")
    f.close()

    print("done")
    return results


if __name__ == "__main__":
    main()
