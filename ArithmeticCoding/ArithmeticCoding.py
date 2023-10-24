import time
import os
from mpmath import *
from collections import Counter


def arithmetic_encode(src):
    max_val, third, qtr, half = 4294967295, 3221225472, 1073741824, 2147483648

    freq = Counter(src)
    prob = {ch: cnt / len(src) for ch, cnt in freq.items()}

    cum_freq = [0.0]
    for p in prob.values():
        cum_freq.append(cum_freq[-1] + p)
    cum_freq.pop()
    cum_freq = {k: v for k, v in zip(prob.keys(), cum_freq)}

    enc_nums = []
    lb, ub = 0, max_val
    strdl = 0

    for b in src:
        rng = ub - lb + 1
        lb += ceil(rng * cum_freq[b])
        ub = lb + floor(rng * prob[b])

        tmp_nums = []
        while True:
            if ub < half:
                tmp_nums.append(0)
                tmp_nums.extend([1] * strdl)
                strdl = 0
            elif lb >= half:
                tmp_nums.append(1)
                tmp_nums.extend([0] * strdl)
                strdl = 0
                lb -= half
                ub -= half
            elif lb >= qtr and ub < third:
                strdl += 1
                lb -= qtr
                ub -= qtr
            else:
                break

            if tmp_nums:
                enc_nums.extend(tmp_nums)
                tmp_nums = []

            lb *= 2
            ub = 2 * ub + 1

    enc_nums.extend([0] + [1] * strdl if lb < qtr else [1] + [0] * strdl)

    return enc_nums


def arithmetic_decode(enc, prob, len_txt):
    p, max_val, third, qtr, half = 32, 4294967295, 3221225472, 1073741824, 2147483648

    alph = list(prob)
    cum_freq = [0]
    for i in prob:
        cum_freq.append(cum_freq[-1] + prob[i])
    cum_freq.pop()

    prob = list(prob.values())

    enc.extend(p * [0])
    dec_sym = len_txt * [0]

    cur_val = int(''.join(str(a) for a in enc[0:p]), 2)
    bit_pos = p
    lb, ub = 0, max_val

    dec_pos = 0
    while 1:
        rng = ub - lb + 1
        sym_idx = len(cum_freq)
        val = (cur_val - lb) / rng
        for i, item in enumerate(cum_freq):
            if item >= val:
                sym_idx = i
                break
        sym_idx -= 1
        dec_sym[dec_pos] = alph[sym_idx]

        lb = lb + ceil(cum_freq[sym_idx] * rng)
        ub = lb + floor(prob[sym_idx] * rng)

        while True:
            if ub < half:
                pass
            elif lb >= half:
                lb -= half
                ub -= half
                cur_val -= half
            elif lb >= qtr and ub < third:
                lb -= qtr
                ub -= qtr
                cur_val -= qtr
            else:
                break

            lb *= 2
            ub = 2 * ub + 1
            cur_val = 2 * cur_val + enc[bit_pos]
            bit_pos += 1
            if bit_pos == len(enc) + 1:
                break

        dec_pos += 1
        if dec_pos == len_txt or bit_pos == len(enc) + 1:
            break
    return bytes(dec_sym)


def encode(fn):
    with open(fn, 'rb') as src:
        inp = src.read()

    freq = dict(Counter(inp))

    enc_seq = arithmetic_encode(inp)
    enc_seq_str = ''.join(map(str, enc_seq))

    pad_cnt = 8 - len(enc_seq_str) % 8
    enc_seq_str += "0" * pad_cnt

    pad_info = "{0:08b}".format(pad_cnt)
    pad_enc_str = pad_info + enc_seq_str

    out_arr = bytearray([int(pad_enc_str[i:i + 8], 2) for i in range(0, len(pad_enc_str), 8)])

    with open(f'{fn}.enc', 'wb') as enc_f:
        enc_f.write(len(inp).to_bytes(4, 'little'))
        enc_f.write((len(freq.keys()) - 1).to_bytes(1, 'little'))

        for b_val, freq in freq.items():
            enc_f.write(b_val.to_bytes(1, 'little'))
            enc_f.write(freq.to_bytes(4, 'little'))

        enc_f.write(bytes(out_arr))


def decode(fn):
    with open(fn, 'rb') as enc_f:
        enc_data = enc_f.read()

    orig_len = int.from_bytes(enc_data[0:4], 'little')
    uniq_cnt = enc_data[4] + 1
    hdr = enc_data[5: 5 * uniq_cnt + 5]

    byte_freq = {}
    for i in range(uniq_cnt):
        b_val = hdr[i * 5]
        freq = int.from_bytes(hdr[i * 5 + 1:i * 5 + 5], 'little')
        byte_freq[b_val] = freq

    probs = {ch: cnt / orig_len for ch, cnt in byte_freq.items()}

    enc_txt = enc_data[5 * (enc_data[4] + 1) + 5:]
    pad_enc_str = ''.join([bin(b)[2:].rjust(8, '0') for b in enc_txt])

    pad_cnt = int(pad_enc_str[:8], 2)
    enc_seq = pad_enc_str[8: -pad_cnt if pad_cnt != 0 else None]
    enc_seq = [int(bit) for bit in enc_seq]

    dec_data = arithmetic_decode(enc_seq, probs, orig_len)

    with open(f'{fn}.dec', 'wb') as dec_f:
        dec_f.write(dec_data)


if __name__ == '__main__':

    choice = input("Вы хотите кодировать(1) или декодировать(0) ваш файл: ")
    file = input("Введите имя файла: ")

    st = time.time()

    if choice == '1':
        encode(file)
        et = time.time()
        t = et - st

        original_file_size = os.path.getsize(file)
        compressed_file_size = os.path.getsize('out.txt')
        compression_ratio = (original_file_size - compressed_file_size) / original_file_size * 100

        print(f"Время кодирования: {t:.4f} сек.")
        print(f"Процент сжатия: {compression_ratio:.2f}%")
    elif choice == '0':
        decode(file)
        et = time.time()
        t = et - st
        print(f"Время декодирования: {t:.4f} сек.")
