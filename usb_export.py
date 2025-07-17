import psutil
import os

def export_to_usb():
    for part in psutil.disk_partitions():
        if 'media' in part.mountpoint.lower() or 'usb' in part.device.lower():
            try:
                for file in os.listdir():
                    if file.endswith(".csv"):
                        src = open(file, 'rb')
                        dst = open(os.path.join(part.mountpoint, file), 'wb')
                        dst.write(src.read())
                        src.close()
                        dst.close()
                return f"Exported CSV files to {part.mountpoint}"
            except Exception as e:
                return f"Export failed: {e}"
    return "No USB drive detected."