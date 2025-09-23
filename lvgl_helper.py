import lvgl as lv

def init_display(lcd):
    HOR_RES = 240
    VER_RES = 240

    buf1 = bytearray(HOR_RES * 40 * 2)
    disp_buf = lv.disp_draw_buf_t()
    disp_buf.init(buf1, None, len(buf1)//2)
    
    disp_drv = lv.disp_drv_t()
    disp_drv.init()
    disp_drv.draw_buf = disp_buf
    disp_drv.flush_cb = lambda drv, area, color_p: st7789_lvgl_flush(lcd, drv, area, color_p)
    disp_drv.hor_res = HOR_RES
    disp_drv.ver_res = VER_RES
    disp_drv.register()

def st7789_lvgl_flush(lcd, drv, area, color_p):
    x1 = area.x1
    y1 = area.y1
    x2 = area.x2
    y2 = area.y2
    lcd.bitmap(x1, y1, x2, y2, color_p)
    drv.flush_ready()

def register_touch(touch):
    indev_drv = lv.indev_drv_t()
    indev_drv.init()
    indev_drv.type = lv.INDEV_TYPE.POINTER
    indev_drv.read_cb = lambda drv, data: gt911_lvgl_read(touch, drv, data)
    indev_drv.register()

def gt911_lvgl_read(touch, drv, data):
    tp = touch.read()
    if tp:
        data.point.x = tp[0]
        data.point.y = tp[1]
        data.state = lv.INDEV_STATE.PR
    else:
        data.state = lv.INDEV_STATE.REL
    return False