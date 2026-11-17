import os
import urllib.request
import json
import zipfile
import shutil

os.makedirs("release_pkg/firmwares", exist_ok=True)
os.makedirs("release_pkg/tools/ite_scripts", exist_ok=True)
os.makedirs("release_pkg/tools/flashrom", exist_ok=True)
os.makedirs("release_pkg/tools/openocd", exist_ok=True)

for f in ("dist/PicoSIO-Flasher.exe", "chips_db.json", "README.md"):
    if os.path.exists(f):
        shutil.copy(f, "release_pkg/")

with open("release_pkg/tools/flashrom/LEEME.txt", "w", encoding="utf-8") as f:
    f.write("Coloca aqui flashrom.exe y sus archivos DLL\n")

def download_file(url, dest):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as out:
            shutil.copyfileobj(r, out)
        print("OK:", dest)
        return True
    except Exception as e:
        print("ERROR:", dest, e)
        return False

download_file(
    "https://github.com",
    "release_pkg/firmwares/debugprobe.uf2"
)
download_file(
    "https://github.com",
    "release_pkg/firmwares/pico_serprog.uf2"
)

if download_file("https://github.com", "ite.zip"):
    with zipfile.ZipFile("ite.zip") as z:
        z.extractall("temp_ite")
    for root, _, files in os.walk("temp_ite"):
        for file in files:
            if file.endswith(".py"):
                shutil.copy(os.path.join(root, file), "release_pkg/tools/ite_scripts/")
            elif file.endswith(".uf2"):
                shutil.copy(os.path.join(root, file), "release_pkg/firmwares/ite_ec.uf2")

try:
    req = urllib.request.Request(
        "https://github.com",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    data = json.loads(urllib.request.urlopen(req).read().decode())
    asset_url = None
    for a in data.get("assets", ()):
        if "win32-x64.zip" in a.get("name", ""):
            asset_url = a.get("browser_download_url")
            break
    if asset_url and download_file(asset_url, "ocd.zip"):
        with zipfile.ZipFile("ocd.zip") as z:
            z.extractall("temp_ocd")
        for folder_name in os.listdir("temp_ocd"):
            top = os.path.join("temp_ocd", folder_name)
            if os.path.isdir(top):
                shutil.copytree(top, "release_pkg/tools/openocd", dirs_exist_ok=True)
                break
except Exception as e:
    print("ERROR OpenOCD:", e)

print("=== RESUMEN FINAL DEL PAQUETE ===")
for root, _, files in os.walk("release_pkg"):
    for file in files:
        print(os.path.join(root, file))

shutil.make_archive("PicoSIO-Flasher-Win64", "zip", "release_pkg")
print("LISTO: PicoSIO-Flasher-Win64.zip creado.")
