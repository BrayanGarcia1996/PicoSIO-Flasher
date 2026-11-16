# PicoSIO Flasher (Windows)

Programador universal de código abierto para chips **Super I/O / Embedded Controller (EC)** utilizando una placa **Raspberry Pi Pico (RP2040 / RP2350)** en Windows.

## Marcas soportadas
* **ITE:** IT8586E, IT8987E, IT8227E, IT5570 (vía SMBus/I2C + secuencia bitbang)
* **ENE:** KB9012, KB9022, KB9028 (vía SPI / serprog)
* **Nuvoton / SMSC:** Series NPCE y MEC (vía SWD / CMSIS-DAP)

## Instrucciones de uso rápido
1. Descarga el paquete compilado desde la pestaña **Actions** (o **Releases**).
2. Coloca los binarios portables de `flashrom.exe` en `tools/flashrom/` y `openocd.exe` en `tools/openocd/` (y `pico_serprog.uf2` en `firmwares/`).
3. Ejecuta `PicoSIO-Flasher.exe`.
4. Selecciona la familia del Super I/O, conecta tu Raspberry Pi Pico presionando el botón **BOOTSEL** y haz clic en **Preparar Pico (Cargar .UF2)**.
5. Realiza las conexiones indicadas en pantalla hacia el conector de teclado o pines del Super I/O.
6. **Importante:** Nunca conectes el pin de 3.3V de la Pico a la placa madre; alimenta la placa con su propio cargador.

## Licencia
Distribuido bajo licencia **GNU General Public License v3.0 (GPL-3.0)**.
