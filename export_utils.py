# vtc/export_utils.py
import os, shutil

def list_usb_mounts():
    candidates = []
    # Common mount roots
    roots = ["/media", "/media/pi", "/run/media", "/run/media/pi", "/mnt"]
    seen = set()
    for r in roots:
        if os.path.isdir(r):
            for name in os.listdir(r):
                p = os.path.join(r, name)
                # consider only dirs that look like mounted devices
                if os.path.ismount(p) and p not in seen:
                    candidates.append(p)
                    seen.add(p)
    return candidates

def export_files(dest_dir, files):
    os.makedirs(dest_dir, exist_ok=True)
    copied = []
    for src in files:
        if src and os.path.isfile(src):
            dst = os.path.join(dest_dir, os.path.basename(src))
            shutil.copy2(src, dst)
            copied.append(dst)
    return copied
