
import os
import hashlib
import filecmp

def get_dir_hash(dir_path):
    if not os.path.exists(dir_path):
        return None
    
    hashes = []
    for root, dirs, files in os.walk(dir_path):
        for file in sorted(files):
            if file.lower().endswith('.tif'):
                path = os.path.join(root, file)
                with open(path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                hashes.append((file, file_hash))
    return hashes

dirs = [
    "images/fvc/DB1_B",
    "images/fvc/DB2_B",
    "images/fvc/DB3_B",
    "images/fvc/DB4_B",
    "images/fvc/DB1_B (1)",
    "images/fvc/DB2_B (1)",
    "images/fvc/DB3_B (1)",
    "images/fvc/DB3_Bj",
    "images/fvc/DB4_B (1)"
]

dir_hashes = {}
print("Computing hashes for datasets...\n")

for d in dirs:
    full_path = os.path.abspath(d)
    print(f"Checking {d}...")
    dh = get_dir_hash(full_path)
    if dh:
        # Create a hash of the directory content to easily compare
        content_sig = hashlib.md5(str(dh).encode()).hexdigest()
        dir_hashes[d] = content_sig
        print(f"  -> Signature: {content_sig}")
    else:
        print(f"  -> Not found")

print("\nDuplicate Sets:")
visited = set()
for d1, h1 in dir_hashes.items():
    if d1 in visited: continue
    duplicates = [d1]
    for d2, h2 in dir_hashes.items():
        if d1 != d2 and h1 == h2:
            duplicates.append(d2)
            visited.add(d2)
    
    if len(duplicates) > 1:
        print(f"Identical group: {duplicates}")
        visited.add(d1)
    else:
        print(f"Unique: {d1}")

