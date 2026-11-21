import zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

pak_path = r"C:\Program Files (x86)\Steam\steamapps\common\OUTRIDERS\Madness\Content\Paks\pakchunk00_s00-WindowsNoEditor_0_P.pak"
aes_key = bytes.fromhex("7638792F423F4528482B4D6251655468576D5A7134743777397A24432646294A")

offset_en = 928555008
compressed_size = 1392000

with open(pak_path, "rb") as f:
    f.seek(offset_en + 24)
    encrypted_data = f.read(compressed_size)

cipher = Cipher(algorithms.AES(aes_key), modes.ECB())
decryptor = cipher.decryptor()
dec = decryptor.update(encrypted_data) + decryptor.finalize()

chunks = []
pos = 0
block = 0

while pos < len(dec):
    # Check if we reached padding / EOF
    if pos + 2 > len(dec) or (dec[pos] != 0x78 and dec[pos] == 0):
        print(f"End of stream reached at pos {pos}/{len(dec)}")
        break

    d = zlib.decompressobj()
    chunk = d.decompress(dec[pos:])
    if not chunk:
        print(f"No chunk decompressed at pos {pos}, stopping.")
        break

    chunks.append(chunk)
    consumed = len(dec[pos:]) - len(d.unused_data)
    # Align consumed to 16 bytes for next block
    consumed_aligned = (consumed + 15) & ~15
    print(f"Block {block:3d}: decompressed {len(chunk):6d} bytes | raw consumed: {consumed:5d} -> aligned: {consumed_aligned:5d} | pos {pos} -> {pos + consumed_aligned}")
    
    pos += consumed_aligned
    block += 1

full_locres = b"".join(chunks)
print(f"\n==========================================")
print(f"TOTAL DECOMPRESSED SIZE: {len(full_locres):,} bytes across {len(chunks)} blocks!")
print(f"==========================================")

out_path = r"C:\Program Files (x86)\Steam\steamapps\common\OUTRIDERS\extracted_loc\Game_en.locres"
with open(out_path, "wb") as f:
    f.write(full_locres)
print(f"Successfully wrote {out_path}!")
