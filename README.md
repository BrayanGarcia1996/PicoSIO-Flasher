# PicoSIO Flasher (Windows)

Programador universal de código abierto para chips **Super I/O / Embedded Controller (EC)** de laptops utilizando una placa **Raspberry Pi Pico (RP2040 / RP2350)** en Windows.

## Características principales
* **Interfaz gráfica unificada:** Olvídate de escribir comandos manuales en consola.
* **Auto-flasheo de la Pico:** Carga automáticamente el firmware `.uf2` adecuado (`ITE`, `serprog` o `Debugprobe`) al conectar la Pico en modo `BOOTSEL`.
* **Detección automática de puerto COM:** Localiza la Raspberry Pi Pico mediante su Vendor ID (`2E8A`).
* **Base de datos de chips y pinouts:** Muestra en pantalla el tamaño de flash esperado y la guía de conexión para los modelos más comunes.
* **Respaldo de seguridad obligatorio:** Realiza una copia automática en la carpeta `backups/` antes de sobrescribir cualquier chip.

## Modelos soportados

| Fabricante | Modelos incluidos | Protocolo | Firmware Pico |
| :--- | :--- | :--- | :--- |
| **ITE** | IT8586E, IT8587E, IT8987E, IT8227E, IT5570E | SMBus / I2C + Bitbang | `ite_ec.uf2` |
| **ENE** | KB9012QF, KB9022Q, KB9028Q | SPI (vía conector teclado) | `pico_serprog.uf2` |
| **Nuvoton / SMSC** | NPCE288, NPCE388, MEC1609, MEC1633 | SWD / JTAG | `debugprobe.uf2` |

## Instalación y puesta en marcha
1. Descarga el archivo **`PicoSIO-Flasher-Win64.zip`** desde la sección **Releases** (o desde la pestaña **Actions**) y descomprímelo.
2. Completa los ejecutables portables externos (por motivos de licencia):
   * Coloca `flashrom.exe` dentro de `tools/flashrom/`.
   * Coloca `openocd.exe` (y sus DLLs/scripts) dentro de `tools/openocd/`.
   * Coloca `pico_serprog.uf2` dentro de `firmwares/`.
3. Ejecuta **`PicoSIO-Flasher.exe`**.

## Advertencia de seguridad eléctrica
* **NUNCA conectes el pin de 3.3V de la Raspberry Pi Pico a la placa madre.**
* Conecta siempre **GND primero** y alimenta la placa base de la laptop utilizando su propio cargador (estado *Standby / Always-On*).

## Licencia
Este proyecto se distribuye bajo la licencia **GNU General Public License v3.0 (GPL-3.0)**.
