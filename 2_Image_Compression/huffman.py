import heapq
import math
from collections import Counter


class Node:
    def __init__(self, symbol, freq, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def build_tree(freq):
    heap = []
    for sym, f in freq.items():
        heap.append(Node(sym, f))
    heapq.heapify(heap)

    if len(heap) == 1:
        return Node(None, heap[0].freq, heap[0], None)

    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, Node(None, a.freq + b.freq, a, b))
    return heap[0]


def get_codes(node, prefix, codes):
    if node.symbol is not None:
        codes[node.symbol] = prefix or "0"
        return
    if node.left is not None:
        get_codes(node.left, prefix + "0", codes)
    if node.right is not None:
        get_codes(node.right, prefix + "1", codes)


def huffman_compress(data):
    freq = Counter(data)
    root = build_tree(freq)
    codes = {}
    get_codes(root, "", codes)

    bits = ""
    for byte in data:
        bits += codes[byte]

    total_bits = len(bits)
    padding = (8 - total_bits % 8) % 8
    bits = bits + "0" * padding
    if bits:
        packed = int(bits, 2).to_bytes(len(bits) // 8, "big")
    else:
        packed = b""

    entropy = 0
    for f in freq.values():
        p = f / len(data)
        entropy -= p * math.log2(p)

    total_len = 0
    for sym, f in freq.items():
        total_len += len(codes[sym]) * f
    avg_len = total_len / len(data)

    info = {
        "root": root,
        "codes": codes,
        "padding": padding,
        "length": len(data),
        "entropy": entropy,
        "avg_code_length": avg_len,
        "total_bits": total_bits,
        "frequencies": dict(freq),
    }
    return packed, info


def huffman_decompress(packed, info):
    if not packed:
        return b""

    bits = bin(int.from_bytes(packed, "big"))[2:]
    bits = bits.zfill(len(packed) * 8)
    if info["padding"]:
        bits = bits[:-info["padding"]]

    root = info["root"]
    node = root
    out = bytearray()
    for bit in bits:
        if bit == "0":
            node = node.left
        else:
            node = node.right
        if node is None:
            continue
        if node.symbol is not None:
            out.append(node.symbol)
            node = root
            if len(out) == info["length"]:
                break
    return bytes(out)
