import os
import subprocess
import datetime

def ensure_backup_dir():
    os.makedirs("backups", exist_ok=True)

def run_command(cmd_list, log_callback):
    """Ejecuta un comando del sistema y envía la salida en tiempo real a la ventana."""
    try:
        log_callback(f"> Ejecutando: {' '.join(cmd_list)}\n")
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        for line in process.stdout:
            log_callback(line)
        process.wait()
        return process.returncode == 0
    except FileNotFoundError:
        log_callback(f"[ERROR] No se encontró la herramienta: {cmd_list[0]}. Verifica la carpeta 'tools/'.\n")
        return False
    except Exception as e:
        log_callback(f"[ERROR] {str(e)}\n")
        return False

def execute_operation(family, action, com_port, file_path, log_callback):
    """Construye el comando según la marca del Super I/O y la acción elegida."""
    ensure_backup_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    if family == "ENE":
        flashrom_exe = os.path.join("tools", "flashrom", "flashrom.exe")
        programmer = f"serprog:dev={com_port}:115200"
        if action == "READ":
            cmd = [flashrom_exe, "-p", programmer, "-r", file_path]
        elif action == "WRITE":
            backup_path = os.path.join("backups", f"ENE_backup_{timestamp}.bin")
            log_callback("Realizando respaldo automático de seguridad antes de escribir...\n")
            if not run_command([flashrom_exe, "-p", programmer, "-r", backup_path], log_callback):
                log_callback("[ABORTADO] Falló el respaldo de seguridad. No se escribió el chip.\n")
                return False
            cmd = [flashrom_exe, "-p", programmer, "-w", file_path]
        elif action == "ERASE":
            cmd = [flashrom_exe, "-p", programmer, "-E"]

    elif family == "ITE":
        ite_script = os.path.join("tools", "ite_scripts", "ite_ec_prog.py")
        if action == "READ":
            cmd = ["python", ite_script, "-p", com_port, "-r", file_path]
        elif action == "WRITE":
            backup_path = os.path.join("backups", f"ITE_backup_{timestamp}.bin")
            log_callback("Realizando respaldo automático de seguridad antes de escribir...\n")
            if not run_command(["python", ite_script, "-p", com_port, "-r", backup_path], log_callback):
                log_callback("[ABORTADO] Falló el respaldo de seguridad.\n")
                return False
            cmd = ["python", ite_script, "-p", com_port, "-w", file_path]
        elif action == "ERASE":
            cmd = ["python", ite_script, "-p", com_port, "-e"]

    elif family == "NUVOTON_SMSC":
        openocd_exe = os.path.join("tools", "openocd", "bin", "openocd.exe")
        if action == "READ":
            cmd = [openocd_exe, "-f", "interface/cmsis-dap.cfg", "-c", f"init; dump_image {file_path} 0x0 0x20000; exit"]
        elif action == "WRITE":
            cmd = [openocd_exe, "-f", "interface/cmsis-dap.cfg", "-c", f"init; reset halt; flash write_image erase {file_path}; reset run; exit"]
        elif action == "ERASE":
            cmd = [openocd_exe, "-f", "interface/cmsis-dap.cfg", "-c", "init; reset halt; flash erase_sector 0 0 last; exit"]

    return run_command(cmd, log_callback)
