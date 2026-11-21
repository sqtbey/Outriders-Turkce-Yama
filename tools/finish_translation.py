import io
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from deep_translator import MyMemoryTranslator

PROPER_NOUNS = [
    # Characters
    'Grand Marshal Corrigan', 'Grand Marshal', 'Corrigan', 'Zahedi', 'Bailey',
    'Channa', 'Shira', 'Jakub', 'August', 'Tiago', 'Kang', 'Seth', 'Moloch',
    'Monroy', 'Yagak', 'Eva Lopez', 'Tanner', 'McCain', 'Jane', 'Victor',
    'Barker', 'Dunlop', 'Giraud', 'Cullen', 'Mercer', 'Lucy', 'Natalie',
    'Audrey', 'Bagram', 'Scurlock', 'Uras', 'Jun', 'Chang', 'Madam Beauvoir',
    'Alastair', 'Wanderer',
    # Locations
    'Trench Town', 'Rift Town', 'First City', 'Deadrock Pass', 'Eagle Peaks',
    'Quarry', 'Forest', 'Pax City', 'Utargak', 'Deserter Camp', 'Ancient Ruins',
    'Dunes', 'Gate', 'Tarya Gratar', 'Caravel', 'Flores', 'Oasis', 'Grand Shrine',
    # Factions & Species
    'ECA', 'Outrider', 'Outriders', 'Altered', 'Insurgents', 'Pax', 'Feral',
    'Ferals', 'Acari', 'Molten Acari', 'Strix', 'Perforo', 'Venomous Perforo',
    'Alpha Perforo', 'Brood Mother', 'Behemoth', 'Chrysaloid',
    # Classes & Lore
    'Devastator', 'Pyromancer', 'Technomancer', 'Trickster', 'Enoch', 'Anomaly',
    'Drop Pod', 'Drop Pod Resources', 'Titanium', 'Iron', 'Leather', 'Shards',
    'World Tier', 'Apocalypse Tier', 'Ascension'
]

ASCII_MAP = {
    'ç': 'c', 'Ç': 'C',
    'ğ': 'g', 'Ğ': 'G',
    'ı': 'i', 'İ': 'I',
    'ö': 'o', 'Ö': 'O',
    'ş': 's', 'Ş': 'S',
    'ü': 'u', 'Ü': 'U'
}

def to_ascii_tr(text):
    if not text:
        return text
    for tr_c, asc_c in ASCII_MAP.items():
        text = text.replace(tr_c, asc_c)
    return text

def protect_string(text):
    tokens = {}
    idx = [0]

    def tag_sub(m):
        tok = f'__T{idx[0]}__'
        idx[0] += 1
        tokens[tok] = m.group(0)
        return tok
    protected = re.sub(r'<[^>]+>', tag_sub, text)

    def fmt_sub(m):
        tok = f'__F{idx[0]}__'
        idx[0] += 1
        tokens[tok] = m.group(0)
        return tok
    protected = re.sub(r'\{[0-9]+\}|\[[A-Za-z0-9_ ]+\]', fmt_sub, protected)

    for pn in sorted(PROPER_NOUNS, key=len, reverse=True):
        pattern = re.compile(rf'\b{re.escape(pn)}\b', re.IGNORECASE)
        def pn_sub(m):
            tok = f'__P{idx[0]}__'
            idx[0] += 1
            tokens[tok] = m.group(0)
            return tok
        protected = pattern.sub(pn_sub, protected)

    return protected, tokens

def restore_string(text, tokens):
    for tok, orig in tokens.items():
        text = text.replace(tok, orig)
    return text

def translate_item(s):
    prot_s, tokens = protect_string(s)
    try:
        t = MyMemoryTranslator(source='en-US', target='tr-TR')
        trans_raw = t.translate(prot_s)
        if trans_raw:
            restored = restore_string(trans_raw, tokens)
            return s, to_ascii_tr(restored)
    except Exception:
        pass
    return s, s

def read_fstring(stream):
    length = struct.unpack('<i', stream.read(4))[0]
    if length == 0:
        return ''
    elif length > 0:
        s = stream.read(length)
        try:
            return s[:-1].decode('utf-8')
        except UnicodeDecodeError:
            return s[:-1].decode('latin1', errors='replace')
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

def build_locres_binary(base_locres_path, translation_map, output_locres_path, use_ascii=True):
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

    stream.seek(str_offset)
    str_count = struct.unpack('<I', stream.read(4))[0]
    orig_strings = []
    for _ in range(str_count):
        s = read_fstring(stream)
        ref = struct.unpack('<i', stream.read(4))[0]
        orig_strings.append((s, ref))

    new_strings = []
    for s, ref in orig_strings:
        if s in translation_map:
            trans_s = translation_map[s]
            if use_ascii:
                trans_s = to_ascii_tr(trans_s)
            new_strings.append((trans_s, ref))
        else:
            new_strings.append((s, ref))

    out = io.BytesIO()
    out.write(magic)
    out.write(bytes([ver]))
    out.write(b'\x00' * 8)

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
    print(f"Generated locres: {output_locres_path} ({len(out.getvalue())} bytes)")

def pack_mod_pak(locres_path, output_pak_path):
    staging_dir = "pak_staging"
    target_rel = os.path.join(staging_dir, "Madness", "Content", "Localization", "Game", "en")
    os.makedirs(target_rel, exist_ok=True)
    shutil.copy2(locres_path, os.path.join(target_rel, "Game.locres"))

    repak_exe = os.path.abspath("repak_bin/repak_outriders.exe")
    cmd = [repak_exe, "pack", "--version", "V9", staging_dir, output_pak_path]
    print(f"Packing patch pak via: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"Successfully generated patch pak: {output_pak_path} ({os.path.getsize(output_pak_path)} bytes)")
    else:
        print(f"Repak error: {res.stderr}")

    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir, ignore_errors=True)

def main():
    json_path = 'extracted_loc/Game_en.json'
    cache_path = 'extracted_loc/translation_cache.json'
    locres_path = 'extracted_loc/Game_en.locres'
    out_locres_path = 'extracted_loc/Game_tr.locres'
    out_pak_extracted = 'extracted_loc/pakchunk00_s00-WindowsNoEditor_1_P.pak'
    out_pak_game = 'Madness/Content/Paks/pakchunk00_s00-WindowsNoEditor_1_P.pak'

    with open(json_path, 'r', encoding='utf-8') as f:
        en_data = json.load(f)

    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        print(f"Loaded {len(cache)} existing cached translations.")

    keep_namespaces = {'Armors_DataTable', 'Weapons_DataTable', 'ItemArtSets_DataTable'}

    missing = []
    for ns, entries in en_data.items():
        if ns in keep_namespaces:
            continue
        for k, text in entries.items():
            if ns == 'ModAssets_DataTable' and (k.endswith('_Name') or k.endswith('_Title') or k.endswith('_Item')):
                continue
            if not text or not text.strip():
                continue
            clean = text.strip()
            if len(clean) == 1 or clean.isdigit() or (clean.startswith('{') and clean.endswith('}')):
                continue
            if text not in cache:
                missing.append(text)

    # Deduplicate while preserving order
    unique_missing = list(dict.fromkeys(missing))
    print(f"Remaining unique strings to translate: {len(unique_missing)}")

    if unique_missing:
        completed = 0
        total = len(unique_missing)
        with ThreadPoolExecutor(max_workers=6) as ex:
            future_to_item = {ex.submit(translate_item, s): s for s in unique_missing}
            for fut in as_completed(future_to_item):
                orig_s, tr_s = fut.result()
                cache[orig_s] = tr_s
                completed += 1
                if completed % 25 == 0 or completed == total:
                    print(f"Progress: [{completed}/{total}] ({(completed/total)*100:.1f}%) | Total cached: {len(cache)}", flush=True)
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump(cache, f, ensure_ascii=False, indent=1)

    print(f"All translations ready! Total cached: {len(cache)}")
    print("Building Turkish locres binary...")
    build_locres_binary(locres_path, cache, out_locres_path, use_ascii=True)

    print("Packaging mod patch pak...")
    pack_mod_pak(out_locres_path, out_pak_extracted)
    shutil.copy2(out_pak_extracted, out_pak_game)
    print(f"Installed patch pak directly to game folder: {out_pak_game}")

if __name__ == '__main__':
    main()
