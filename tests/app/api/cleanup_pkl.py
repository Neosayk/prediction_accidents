import os
from pathlib import Path

target_dir = Path("src/app/api/")
pkl_files = list(target_dir.glob("*.pkl"))
pkl_files.sort(key=os.path.getmtime)
if len(pkl_files) > 2:
    for file in pkl_files[:-2]:
        file.unlink()