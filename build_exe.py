"""
Build helper script for BotMyPC.
Compiles the application into a standalone Windows executable using PyInstaller.
"""

import subprocess
import sys
from pathlib import Path


def build():
    root_dir = Path(__file__).resolve().parent
    spec_file = root_dir / "botmypc.spec"

    print(f"Compiling {spec_file.name} with PyInstaller...")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "-y",
        str(spec_file),
    ]

    res = subprocess.run(cmd, cwd=str(root_dir))
    if res.returncode == 0:
        print("\n[SUCCESS] Build completata con successo!")
        print(f"L'eseguibile si trova in: {root_dir / 'dist' / 'BotMyPC.exe'}")
    else:
        print(f"\n[ERROR] Build fallita con codice di uscita {res.returncode}")
        sys.exit(res.returncode)


if __name__ == "__main__":
    build()
