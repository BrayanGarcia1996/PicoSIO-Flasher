import os
import urllib.request
import json
import zipfile
import shutil

os.makedirs("release_pkg/firmwares", exist_ok=True)
os.makedirs("release_pkg/tools/ite_scripts", exist_ok=True)
os.makedirs("release_pkg/tools/flashrom", exist_ok=True)
os.makedirs("release_pkg/tools/openocd", exist_ok=True)

for f in ["dist/PicoSIO-Flasher.exe", "chips_db.json", "README.md"]:
    if os.path.exists(f):
        shutil.copy(f, "release_pkg/")

with open("release_pkg/tools/flashrom/LEEME.txt", "w", encoding="utf-8") as f:
    f.write("Coloca aqui flashrom.exe y sus archivos DLL\n")

def download_file(url, dest):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as out:
            shutil.copyfileobj(r, out)
        print("[OK]", dest)
        return True
    except Exception as e:
        print("[ERROR]", dest, e)
        return False

# 1. Debugprobe y pico_serprog
download_file(
    "https://github.com",
    "release_pkg/firmwares/debugprobe.uf2"
)
download_file(
    "https://github.com",
    "release_pkg/firmwares/pico_serprog.uf2"
)

# 2. Scripts y firmware ITE (rama master)
if download_file("https://github.com", "ite.zip"):
    with zipfile.ZipFile("ite.zip") as z:
        z.extractall("temp_ite")
    for root, _, files in os.walk("temp_ite"):
        for file in files:
            if file.endswith(".py"):
                shutil.copy(os.path.join(root, file), "release_pkg/tools/ite_scripts/")
            elif file.endswith(".uf2"):
                shutil.copy(os.path.join(root, file), "release_pkg/firmwares/ite_ec.uf2")

# 3. Ultima version de OpenOCD Windows desde xPack
try:
    req = urllib.request.Request(
        "https://github.com",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    data = json.loads(urllib.request.urlopen(req).read().decode())
    asset = next((a["browser_download_url"] for a in data.get("assets", []) if "win32-x64.zip" in a["name"]), None)
    if asset and download_file(asset, "ocd.zip"):
        with zipfile.ZipFile("ocd.zip") as z:
            z.extractall("temp_ocd")
        folders = os.listdir("temp_ocd")
        if folders:
            top = os.path.join("temp_ocd", folders[0])
            shutil.copytree(top, "release_pkg/tools/openocd", dirs_exist_ok=True)
except Exception as e:
    print("[ERROR] OpenOCD:", e)

print("=== RESUMEN FINAL DEL PAQUETE ===")
for root, _, files in os.walk("release_pkg"):
    for file in files:
        print(os.path.join(root, file))

shutil.make_archive("PicoSIO-Flasher-Win64", "zip", "release_pkg")
print("[LISTO] PicoSIO-Flasher-Win64.zip creado.")
