# Using Pre-existing MicroPython LVGL Fork for ESP32-S3

This folder provides instructions for building and flashing firmware from a fork of MicroPython with LVGL support.

---

## Recommended Fork

- [lvgl/lv_micropython](https://github.com/lvgl/lv_micropython) (actively maintained LVGL integration)

---

## Steps

1. Clone the Fork:
    ```sh
    git clone https://github.com/lvgl/lv_micropython.git
    cd lv_micropython
    git submodule update --init --recursive
    ```

2. Set up ESP-IDF (see instructions above).

3. Build for ESP32-S3:
    ```sh
    cd ports/esp32
    idf.py set-target esp32s3
    idf.py build
    ```

4. Firmware Output:
    - Check the `build/` folder for the `.bin` file.
    - Upload your compiled `.bin` to `/firmware-bin/` in this repository.

---

## Upload Instructions

- Place your compiled LVGL-enabled MicroPython firmware here:  
  `/firmware-bin/micropython_lvgl_esp32s3.bin`

---

## Useful Links

- [lv_micropython Wiki](https://github.com/lvgl/lv_micropython/wiki)
- [ESP-IDF Official Docs](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/index.html)