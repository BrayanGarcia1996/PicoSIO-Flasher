import os
import json
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pico_manager import flash_pico_firmware, find_pico_com_port
from runners import execute_operation

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEFAULT_DB = {
    "ITE": {"IT8586E (128 KB)": {"size": "128 KB", "pinout": "GP0->SDA | GP1->SCL | GP2->KSI6 | GND->GND"}},
    "ENE": {"KB9012QF (128 KB)": {"size": "128 KB", "pinout": "GP16->MISO | GP17->CS | GP18->SCK | GP19->MOSI | GND->GND+KSI7"}},
    "NUVOTON_SMSC": {"NPCE288 (256 KB)": {"size": "256 KB", "pinout": "GP2->SWCLK | GP3->SWDIO | GP4->RESET | GND->GND"}}
}

def load_chips_db():
    if os.path.exists("chips_db.json"):
        try:
            with open("chips_db.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_DB

class PicoSIOApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PicoSIO Flasher v1.0 - Programador Universal Super I/O")
        self.geometry("800x600")
        self.resizable(False, False)
        self.selected_file = ""
        self.chips_db = load_chips_db()

        # Título
        self.header = ctk.CTkLabel(self, text="PicoSIO Flasher (Raspberry Pi Pico)", font=("Segoe UI", 20, "bold"))
        self.header.pack(pady=10)

        # Frame Superior: Selección de Familia y Modelo
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(self.top_frame, text="1. Familia:", font=("Segoe UI", 13, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.family_var = ctk.StringVar(value="ITE")
        self.family_menu = ctk.CTkOptionMenu(self.top_frame, values=list(self.chips_db.keys()), variable=self.family_var, command=self.on_family_change, width=150)
        self.family_menu.grid(row=0, column=1, padx=5, pady=10)

        ctk.CTkLabel(self.top_frame, text="2. Modelo Chip:", font=("Segoe UI", 13, "bold")).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        initial_models = list(self.chips_db["ITE"].keys())
        self.model_var = ctk.StringVar(value=initial_models[0])
        self.model_menu = ctk.CTkOptionMenu(self.top_frame, values=initial_models, variable=self.model_var, command=self.on_model_change, width=260)
        self.model_menu.grid(row=0, column=3, padx=5, pady=10)

        # Fila 2 del Frame Superior: Botones Pico
        self.btn_flash_pico = ctk.CTkButton(self.top_frame, text="Preparar Pico (Cargar .UF2)", fg_color="#D97706", hover_color="#B45309", command=self.flash_pico)
        self.btn_flash_pico.grid(row=1, column=0, columnspan=2, padx=10, pady=8, sticky="ew")

        self.btn_detect = ctk.CTkButton(self.top_frame, text="Detectar Puerto COM", command=self.detect_port)
        self.btn_detect.grid(row=1, column=2, columnspan=2, padx=10, pady=8, sticky="ew")

        # Guía de Pinout y Tamaño de Flash
        self.pinout_label = ctk.CTkLabel(self, text="", justify="left", font=("Consolas", 12), fg_color="#1E293B", corner_radius=8, padx=15, pady=10)
        self.pinout_label.pack(fill="x", padx=20, pady=8)
        self.on_model_change(initial_models[0])

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
        self.console = ctk.CTkTextbox(self, height=150, font=("Consolas", 12))
        self.console.pack(fill="both", expand=True, padx=20, pady=10)
        self.log("Sistema listo. Selecciona la familia y modelo de Super I/O.\n")

    def log(self, text):
        self.console.insert("end", text)
        self.console.see("end")

    def on_family_change(self, family):
        models = list(self.chips_db.get(family, {}).keys())
        self.model_menu.configure(values=models)
        if models:
            self.model_var.set(models[0])
            self.on_model_change(models[0])

    def on_model_change(self, model):
        family = self.family_var.get()
        info = self.chips_db.get(family, {}).get(model, {})
        size_txt = info.get("size", "Desconocido")
        pinout_txt = info.get("pinout", "")
        self.pinout_label.configure(text=f"TAMAÑO FLASH ESPERADO: {size_txt}\n{pinout_txt}")

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
            size_kb = os.path.getsize(path) / 1024
            self.selected_file = path
            self.file_label.configure(text=f"{os.path.basename(path)} ({size_kb:.1f} KB)", text_color="white")

    def start_task(self, action):
        family = self.family_var.get()
        port = find_pico_com_port()
        if not port and family == "ENE":
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
        self.log(f"\n--- Iniciando operación {action} para {self.model_var.get()} ---\n")
        success = execute_operation(family, action, port, target_file, self.log)
        if success:
            self.log(f"[ÉXITO] Operación {action} completada correctamente.\n")
        else:
            self.log(f"[FALLO] La operación {action} terminó con errores.\n")

if __name__ == "__main__":
    app = PicoSIOApp()
    app.mainloop()
