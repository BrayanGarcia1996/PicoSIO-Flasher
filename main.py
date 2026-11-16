import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pico_manager import flash_pico_firmware, find_pico_com_port
from runners import execute_operation

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PINOUT_GUIDES = {
    "ITE": "CONEXIÓN ITE (SMBus/I2C):\n• GP0 -> SDA (KSI4)\n• GP1 -> SCL (KSI5)\n• GP2 -> Activación (KSI6/KSI7)\n• GND -> GND Placa\n* Alimentar placa con su cargador.",
    "ENE": "CONEXIÓN ENE KB90xx (SPI):\n• GP16 -> MISO (KSI4)\n• GP17 -> CS (KSO3)\n• GP18 -> SCK (KSI5)\n• GP19 -> MOSI (KSI6)\n• GND -> GND Placa + Pin EDI_CS",
    "NUVOTON_SMSC": "CONEXIÓN NUVOTON / SMSC (SWD):\n• GP2 -> SWCLK / TCK\n• GP3 -> SWDIO / TMS\n• GP4 -> RESET\n• GND -> GND Placa\n* Usar Debugprobe CMSIS-DAP."
}

class PicoSIOApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PicoSIO Flasher v1.0 - Programador Universal Super I/O")
        self.geometry("760x560")
        self.resizable(False, False)
        self.selected_file = ""

        # Título
        self.header = ctk.CTkLabel(self, text="PicoSIO Flasher (Raspberry Pi Pico)", font=("Segoe UI", 20, "bold"))
        self.header.pack(pady=10)

        # Frame Superior: Selección de Familia y Firmware Pico
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.top_frame, text="1. Familia Super I/O:", font=("Segoe UI", 13, "bold")).grid(row=0, column=0, padx=10, pady=10)
        self.family_var = ctk.StringVar(value="ITE")
        self.family_menu = ctk.CTkOptionMenu(self.top_frame, values=["ITE", "ENE", "NUVOTON_SMSC"], variable=self.family_var, command=self.update_pinout)
        self.family_menu.grid(row=0, column=1, padx=10, pady=10)

        self.btn_flash_pico = ctk.CTkButton(self.top_frame, text="Preparar Pico (Cargar .UF2)", fg_color="#D97706", hover_color="#B45309", command=self.flash_pico)
        self.btn_flash_pico.grid(row=0, column=2, padx=10, pady=10)

        self.btn_detect = ctk.CTkButton(self.top_frame, text="Detectar Puerto COM", command=self.detect_port)
        self.btn_detect.grid(row=0, column=3, padx=10, pady=10)

        # Guía de Pinout
        self.pinout_label = ctk.CTkLabel(self, text=PINOUT_GUIDES["ITE"], justify="left", font=("Consolas", 12), fg_color="#1E293B", corner_radius=8, padx=15, pady=10)
        self.pinout_label.pack(fill="x", padx=20, pady=8)

        # Selección de Archivo Binario
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.pack(fill="x", padx=20, pady=5)

        self.btn_select_file = ctk.CTkButton(self.file_frame, text="Seleccionar Archivo (.BIN / .ROM)", command=self.choose_file)
        self.btn_select_file.pack(side="left", padx=10, pady=10)

        self.file_label = ctk.CTkLabel(self.file_frame, text="Ningún archivo seleccionado", text_color="gray")
        self.file_label.pack(side="left", padx=10)

        # Botones de Acción
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.pack(fill="x", padx=20, pady=8)

        self.btn_read = ctk.CTkButton(self.action_frame, text="LEER CHIP (Backup)", fg_color="#059669", hover_color="#047857", command=lambda: self.start_task("READ"))
        self.btn_read.pack(side="left", expand=True, padx=10, pady=10)

        self.btn_write = ctk.CTkButton(self.action_frame, text="ESCRIBIR CHIP", fg_color="#2563EB", hover_color="#1D4ED8", command=lambda: self.start_task("WRITE"))
        self.btn_write.pack(side="left", expand=True, padx=10, pady=10)

        self.btn_erase = ctk.CTkButton(self.action_frame, text="BORRAR CHIP", fg_color="#DC2626", hover_color="#B91C1C", command=lambda: self.start_task("ERASE"))
        self.btn_erase.pack(side="left", expand=True, padx=10, pady=10)

        # Consola de Salida
        self.console = ctk.CTkTextbox(self, height=160, font=("Consolas", 12))
        self.console.pack(fill="both", expand=True, padx=20, pady=10)
        self.log("Sistema listo. Selecciona la marca del Super I/O y conecta tu Raspberry Pi Pico.\n")

    def log(self, text):
        self.console.insert("end", text)
        self.console.see("end")

    def update_pinout(self, choice):
        self.pinout_label.configure(text=PINOUT_GUIDES.get(choice, ""))

    def flash_pico(self):
        family = self.family_var.get()
        self.log(f"Buscando Pico en modo BOOTSEL para cargar firmware {family}...\n")
        ok, msg = flash_pico_firmware(family)
        self.log(msg + "\n")

    def detect_port(self):
        port = find_pico_com_port()
        if port:
            self.log(f"[OK] Raspberry Pi Pico detectada en el puerto: {port}\n")
        else:
            self.log("[AVISO] No se detectó ningún puerto COM de Raspberry Pi Pico.\n")

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos Binarios", "*.bin *.rom"), ("Todos los archivos", "*.*")])
        if path:
            self.selected_file = path
            self.file_label.configure(text=os.path.basename(path), text_color="white")

    def start_task(self, action):
        family = self.family_var.get()
        port = find_pico_com_port()
        if not port and family != "NUVOTON_SMSC":
            messagebox.showerror("Error", "Conecta la Raspberry Pi Pico primero (no se detectó puerto COM).")
            return

        if action == "READ":
            save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Archivo Binario", "*.bin")])
            if not save_path:
                return
            target_file = save_path
        elif action == "WRITE":
            if not self.selected_file:
                messagebox.showwarning("Aviso", "Selecciona primero el archivo .BIN que deseas grabar.")
                return
            target_file = self.selected_file
        else:
            target_file = ""

        threading.Thread(target=self._run_worker, args=(family, action, port, target_file), daemon=True).start()

    def _run_worker(self, family, action, port, target_file):
        self.log(f"\n--- Iniciando operación {action} para {family} ---\n")
        success = execute_operation(family, action, port, target_file, self.log)
        if success:
            self.log(f"[ÉXITO] Operación {action} completada correctamente.\n")
        else:
            self.log(f"[FALLO] La operación {action} terminó con errores.\n")

if __name__ == "__main__":
    app = PicoSIOApp()
    app.mainloop()
