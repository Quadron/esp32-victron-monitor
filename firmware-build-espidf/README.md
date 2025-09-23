# ESP-IDF + CMake MicroPython Build with LVGL for ESP32-S3

This folder helps you build your own MicroPython firmware for ESP32-S3 with LVGL support using ESP-IDF and CMake.

---

## Prerequisites

- ESP-IDF v5.0+ ([Install guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/index.html))
- Python 3.7+
- Git

---

## Steps

### 1. Install ESP-IDF

- Follow the official Espressif guide: [ESP-IDF Setup Guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/index.html)
- Run the install and export scripts as described for your OS.

### 2. Clone MicroPython and LVGL

```sh
git clone https://github.com/micropython/micropython.git
cd micropython
git submodule update --init --recursive
```

#### (Optional) Use LVGL MicroPython Fork:
Instead of adding LVGL manually, you can use the fork in `micropython-lvgl-fork/` for easier setup (see that folder).

### 3. Add LVGL to your MicroPython build

- LVGL is usually included as a submodule in `micropython/lib/lvgl`
- For advanced use, clone [lvgl/lv_micropython](https://github.com/lvgl/lv_micropython) and follow their instructions.

### 4. Copy Example Configuration

Copy `sdkconfig.defaults` from this folder into `micropython/ports/esp32/`.

### 5. Build Firmware

```sh
cd micropython/ports/esp32
idf.py set-target esp32s3
idf.py menuconfig   # (optional, for hardware tweaks)
idf.py build
```

### 6. Find Your Firmware

- The `.bin` file will be in `micropython/ports/esp32/build/`
- Copy it to your repo’s `/firmware-bin/` folder.

---

## Upload Instructions

- Place your compiled `.bin` firmware here:  
  `/firmware-bin/micropython_lvgl_esp32s3.bin`

---

## Flashing Your Device

1. Plug in your ESP32-S3 board.
2. Download [esptool.py](https://github.com/espressif/esptool).
3. Erase the chip:
    ```sh
    esptool.py --chip esp32s3 erase_flash
    ```
4. Flash your firmware:
    ```sh
    esptool.py --chip esp32s3 --port /dev/ttyUSB0 write_flash -z 0x0 firmware-bin/micropython_lvgl_esp32s3.bin
    ```
   (_Replace `/dev/ttyUSB0` with your actual COM port._)

---

## Troubleshooting

- If you get errors:
  - Double-check Python, Git, and ESP-IDF are installed.
  - Make sure you’re using the right command line for your OS.
  - Check MicroPython and LVGL documentation.
  - Ask for help in the MicroPython or LVGL forums!

---

## References

- [MicroPython ESP32 port](https://github.com/micropython/micropython/tree/master/ports/esp32)
- [LVGL MicroPython](https://github.com/lvgl/lv_micropython)