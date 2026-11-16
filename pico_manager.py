import os
import time
import shutil
import psutil
import serial.tools.list_ports

# Vendor ID oficial de Raspberry Pi (RP2040 / RP2350)
PICO_VID = 0x2E8A

FIRMWARE_MAP = {
    "ITE": "firmwares/ite_ec.uf2",
    "ENE": "firmwares/pico_serprog.uf2",
    "NUVOTON_SMSC": "firmwares/debugprobe.uf2"
}

def find_bootsel_drive():
    """Busca en Windows la unidad llamada RPI-RP2."""
    for partition in psutil.disk_partitions(all=False):
        if 'removable' in partition.opts.lower() or partition.fstype == 'FAT':
            try:
                drive_path = partition.mountpoint
                info_file = os.path.join(drive_path, "INFO_UF2.TXT")
                if os.path.exists(info_file):
                    return drive_path
            except Exception:
                continue
    return None

def flash_pico_firmware(chip_family):
    """Copia el archivo .uf2 correspondiente a la unidad RPI-RP2."""
    uf2_path = FIRMWARE_MAP.get(chip_family)
    if not uf2_path or not os.path.exists(uf2_path):
        return False, f"No se encontró el archivo de firmware: {uf2_path}"

    drive = find_bootsel_drive()
    if not drive:
        return False, "Pico en modo BOOTSEL no detectada. Conéctala presionando el botón BOOTSEL."

    try:
        dest = os.path.join(drive, os.path.basename(uf2_path))
        shutil.copyfile(uf2_path, dest)
        time.sleep(3)
        return True, f"Firmware {os.path.basename(uf2_path)} cargado correctamente."
    except Exception as e:
        return False, f"Error al copiar firmware: {str(e)}"

def find_pico_com_port():
    """Detecta automáticamente el puerto COM asignado a la Raspberry Pi Pico en Windows."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.vid == PICO_VID:
            return port.device
    return None
