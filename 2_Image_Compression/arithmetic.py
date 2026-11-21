from collections import Counter

MAX_RANGE = 1 << 32
HALF = MAX_RANGE // 2
QUARTER = HALF // 2
THREE_QUARTER = 3 * QUARTER


class BitWriter:
    def __init__(self):
        self.data = bytearray()
        self.acc = 0
        self.count = 0
        self.total_bits = 0

    def write(self, bit):
        self.acc = (self.acc << 1) | bit
        self.count += 1
        self.total_bits += 1
        if self.count == 8:
            self.data.append(self.acc)
            self.acc = 0
            self.count = 0

    def finish(self):
        if self.count:
            self.data.append(self.acc << (8 - self.count))
        return bytes(self.data)


class BitReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read(self):
        if self.pos // 8 >= len(self.data):
            return 0
        bit = (self.data[self.pos // 8] >> (7 - self.pos % 8)) & 1
        self.pos += 1
        return bit


def build_model(data):
    freq = Counter(data)
    cum = {}
    total = 0
    for sym in sorted(freq):
        cum[sym] = (total, total + freq[sym])
        total += freq[sym]
    ranges = []
    for sym, (lo, hi) in cum.items():
        ranges.append((lo, hi, sym))
    return cum, ranges, total, dict(freq)


def arithmetic_compress(data):
    cum, ranges, total, freq = build_model(data)
    writer = BitWriter()
    low = 0
    high = MAX_RANGE
    pending = 0

    def emit(bit):
        nonlocal pending
        writer.write(bit)
        while pending:
            writer.write(1 - bit)
            pending -= 1

    for sym in data:
        lo_c, hi_c = cum[sym]
        rng = high - low
        high = low + rng * hi_c // total
        low = low + rng * lo_c // total

        while True:
            if high <= HALF:
                emit(0)
                low = low * 2
                high = high * 2
            elif low >= HALF:
                emit(1)
                low = (low - HALF) * 2
                high = (high - HALF) * 2
            elif low >= QUARTER and high <= THREE_QUARTER:
                pending += 1
                low = (low - QUARTER) * 2
                high = (high - QUARTER) * 2
            else:
                break

    pending += 1
    if low < QUARTER:
        emit(0)
    else:
        emit(1)

    packed = writer.finish()
    info = {
        "cum": cum,
        "ranges": ranges,
        "total": total,
        "length": len(data),
        "frequencies": freq,
        "total_bits": writer.total_bits,
    }
    return packed, info


def arithmetic_decompress(packed, info):
    ranges = info["ranges"]
    total = info["total"]
    length = info["length"]

    reader = BitReader(packed)
    low = 0
    high = MAX_RANGE
    value = 0
    for i in range(32):
        value = (value << 1) | reader.read()

    out = bytearray()
    for i in range(length):
        rng = high - low
        scaled = ((value - low + 1) * total - 1) // rng
        for lo_c, hi_c, sym in ranges:
            if lo_c <= scaled < hi_c:
                out.append(sym)
                high = low + rng * hi_c // total
                low = low + rng * lo_c // total
                break

        while True:
            if high <= HALF:
                low = low * 2
                high = high * 2
            elif low >= HALF:
                low = (low - HALF) * 2
                high = (high - HALF) * 2
            elif low >= QUARTER and high <= THREE_QUARTER:
                low = (low - QUARTER) * 2
                high = (high - QUARTER) * 2
                value = value - QUARTER
            else:
                break
            value = ((value << 1) & (MAX_RANGE - 1)) | reader.read()

    return bytes(out)
