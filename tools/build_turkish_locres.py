import struct
import io
import json
import os
import sys

def read_fstring(stream):
    length = struct.unpack('<i', stream.read(4))[0]
    if length == 0:
        return ''
    elif length > 0:
        s = stream.read(length)
        return s[:-1].decode('latin1')
    else:
        utf16_len = -length
        s = stream.read(utf16_len * 2)
        return s[:-2].decode('utf-16-le', errors='replace')

def write_fstring(s):
    if s == '':
        return struct.pack('<i', 1) + b'\x00'
    is_pure_ascii = all(ord(c) <= 127 for c in s)
    if is_pure_ascii:
        b = s.encode('latin1') + b'\x00'
        return struct.pack('<i', len(b)) + b
    else:
        b = s.encode('utf-16-le') + b'\x00\x00'
        return struct.pack('<i', -(len(b) // 2)) + b

def to_ascii_tr(text):
    if not text:
        return text
    mapping = {
        'ç': 'c', 'Ç': 'C',
        'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I',
        'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S',
        'ü': 'u', 'Ü': 'U'
    }
    for tr_c, asc_c in mapping.items():
        text = text.replace(tr_c, asc_c)
    return text

def build_locres(base_locres_path, translation_dict, output_locres_path, use_ascii=True):
    with open(base_locres_path, 'rb') as f:
        data = f.read()

    stream = io.BytesIO(data)
    magic = stream.read(16)
    ver = stream.read(1)[0]
    str_offset = struct.unpack('<q', stream.read(8))[0]

    entries_count = struct.unpack('<I', stream.read(4))[0]
    ns_count = struct.unpack('<I', stream.read(4))[0]
    namespaces = []

    for _ in range(ns_count):
        ns_hash = struct.unpack('<I', stream.read(4))[0]
        ns_str = read_fstring(stream)
        key_count = struct.unpack('<I', stream.read(4))[0]
        keys = []
        for _ in range(key_count):
            k_hash = struct.unpack('<I', stream.read(4))[0]
            k_str = read_fstring(stream)
            src_hash = struct.unpack('<I', stream.read(4))[0]
            str_idx = struct.unpack('<i', stream.read(4))[0]
            keys.append((k_hash, k_str, src_hash, str_idx))
        namespaces.append((ns_hash, ns_str, keys))

    # Read original strings table
    stream.seek(str_offset)
    str_count = struct.unpack('<I', stream.read(4))[0]
    orig_strings = []
    for _ in range(str_count):
        s = read_fstring(stream)
        ref = struct.unpack('<i', stream.read(4))[0]
        orig_strings.append((s, ref))

    # Translate strings
    new_strings = []
    for s, ref in orig_strings:
        if s in translation_dict:
            trans_s = translation_dict[s]
            if use_ascii:
                trans_s = to_ascii_tr(trans_s)
            new_strings.append((trans_s, ref))
        else:
            new_strings.append((s, ref))

    # Serialize new locres
    out = io.BytesIO()
    out.write(magic)
    out.write(bytes([ver]))
    out.write(b'\x00' * 8) # Placeholder for string offset

    out.write(struct.pack('<I', entries_count))
    out.write(struct.pack('<I', ns_count))
    for ns_hash, ns_str, keys in namespaces:
        out.write(struct.pack('<I', ns_hash))
        out.write(write_fstring(ns_str))
        out.write(struct.pack('<I', len(keys)))
        for k_hash, k_str, src_hash, str_idx in keys:
            out.write(struct.pack('<I', k_hash))
            out.write(write_fstring(k_str))
            out.write(struct.pack('<I', src_hash))
            out.write(struct.pack('<i', str_idx))

    new_str_offset = out.tell()
    out.seek(17)
    out.write(struct.pack('<q', new_str_offset))
    out.seek(new_str_offset)

    out.write(struct.pack('<I', len(new_strings)))
    for s, ref in new_strings:
        out.write(write_fstring(s))
        out.write(struct.pack('<i', ref))

    os.makedirs(os.path.dirname(output_locres_path), exist_ok=True)
    with open(output_locres_path, 'wb') as f:
        f.write(out.getvalue())
    print(f"Successfully generated {output_locres_path} ({len(out.getvalue())} bytes)")

if __name__ == '__main__':
    base = sys.argv[1] if len(sys.argv) > 1 else 'extracted_loc/Game_en.locres'
    trans = sys.argv[2] if len(sys.argv) > 2 else 'extracted_loc/Game_tr_dict.json'
    out = sys.argv[3] if len(sys.argv) > 3 else 'extracted_loc/Game_tr.locres'
    
    if os.path.exists(trans):
        with open(trans, 'r', encoding='utf-8') as f:
            d = json.load(f)
    else:
        d = {}
    build_locres(base, d, out, use_ascii=True)
