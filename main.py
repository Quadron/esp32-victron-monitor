
import time
import lvgl as lv
from micropython_mqtt import MQTTClient
from ui_config import MQTT_TOPICS, SCREENS
from network_config import connect_network

MQTT_BROKER = "192.168.1.100"  # <-- your Cebro GX IP
MQTT_PORT = 1883
MQTT_CLIENT_ID = "esp32s3_display"

# ESP32-S3-LCD-1.28-B pin mapping for LCD and touch
LCD_CS   = 4
LCD_DC   = 6
LCD_RST  = 48
LCD_BL   = 5
LCD_SCK  = 7
LCD_MOSI = 15

TP_SCK   = 17
TP_MOSI  = 18
TP_IRQ   = 21

network_connected = False
mqtt_connected = False

# --- DISPLAY SETUP (ST7789 240x240 round) ---
import st7789
import lvgl_helper

spi_lcd = machine.SoftSPI(sck=machine.Pin(LCD_SCK), mosi=machine.Pin(LCD_MOSI), miso=None)
lcd = st7789.ST7789(
    spi_lcd,
    240,
    240,
    reset=machine.Pin(LCD_RST, machine.Pin.OUT),
    dc=machine.Pin(LCD_DC, machine.Pin.OUT),
    cs=machine.Pin(LCD_CS, machine.Pin.OUT),
    backlight=machine.Pin(LCD_BL, machine.Pin.OUT),
    rotation=0
)

lcd.init()
lcd.backlight_on()

lv.init()
lvgl_helper.init_display(lcd)

# --- TOUCH SETUP (GT911 I2C) ---
from gt911 import GT911

i2c_touch = machine.I2C(1, scl=machine.Pin(TP_SCK), sda=machine.Pin(TP_MOSI), freq=400000)
touch = GT911(i2c_touch, int_pin=TP_IRQ)
lvgl_helper.register_touch(touch)

# --- DATA STORAGE ---
# Dynamically create mqtt_data from topics
mqtt_data = {t['topic']: "--" for t in MQTT_TOPICS}

# --- LVGL UI: MULTI-PAGE, DARK ROUND STYLE ---
def color(hexstr):  # helper for LVGL color
    return lv.color_hex(int(hexstr, 16))

# Victron dark style colors
COLOR_BG = color("23272A")  # dark background
COLOR_ACCENT = color("0099FF")  # blue accent
COLOR_PANEL = color("2C2F33")  # panel
COLOR_GREEN = color("30C67C")
COLOR_ORANGE = color("F4A300")
COLOR_GREY = color("CCCCCC")
COLOR_WHITE = color("FFFFFF")

def create_round_panel(parent, title, value, unit="", color_val=COLOR_ACCENT):
    panel = lv.obj(parent)
    panel.set_size(200, 200)
    panel.set_pos(20, 20)
    panel.set_style_bg_color(COLOR_PANEL, 0)
    panel.set_style_radius(100, 0)
    panel.set_style_border_width(4, 0)
    panel.set_style_border_color(color_val, 0)

    lbl_title = lv.label(panel)
    lbl_title.set_text(title)
    lbl_title.set_style_text_color(COLOR_ACCENT, 0)
    lbl_title.set_style_text_font(lv.font_montserrat_16, 0)
    lbl_title.set_pos(60, 30)

    lbl_val = lv.label(panel)
    lbl_val.set_text(value)
    lbl_val.set_style_text_color(color_val, 0)
    lbl_val.set_style_text_font(lv.font_montserrat_32, 0)
    lbl_val.set_pos(70, 80)

    lbl_unit = lv.label(panel)
    lbl_unit.set_text(unit)
    lbl_unit.set_style_text_color(COLOR_GREY, 0)
    lbl_unit.set_style_text_font(lv.font_montserrat_16, 0)
    lbl_unit.set_pos(90, 120)

    return panel, lbl_val


# --- Dynamic DataPages class using SCREENS and MQTT_TOPICS ---
class DataPages:
    def __init__(self):
        self.pages = []
        self.current = 0
        self.container = lv.obj()
        self.container.set_size(240,240)
        self.container.set_pos(0,0)
        self.labels = {}  # {topic: label_obj}
        self.tank_meter = None
        self.create_pages()
        lv.scr_load(self.container)
        self.show_page(0)
        self.container.add_event_cb(self.handle_swipe, lv.EVENT.GESTURE, None)

    def create_pages(self):
        color_map = {
            "green": COLOR_GREEN,
            "orange": COLOR_ORANGE,
            "accent": COLOR_ACCENT,
            "grey": COLOR_GREY,
            "white": COLOR_WHITE
        }
        for screen in SCREENS:
            page = lv.obj(self.container)
            page.set_size(240,240)
            page.set_style_bg_color(COLOR_BG, 0)
            page.set_style_radius(120, 0)
            y_offset = 30
            for idx, topic_name in enumerate(screen["topics"]):
                topic_cfg = next((t for t in MQTT_TOPICS if t["topic"] == topic_name), None)
                if not topic_cfg:
                    continue
                color_val = color_map.get(topic_cfg.get("color", "accent"), COLOR_ACCENT)
                if screen["name"] == "Tank":
                    # Special round meter for tank
                    self.tank_meter = lv.arc(page)
                    self.tank_meter.set_size(180,180)
                    self.tank_meter.set_pos(30,30)
                    self.tank_meter.set_style_bg_color(COLOR_PANEL, 0)
                    self.tank_meter.set_style_arc_color(COLOR_ACCENT, lv.PART.INDICATOR)
                    self.tank_meter.set_style_arc_width(20, lv.PART.INDICATOR)
                    self.tank_meter.set_style_arc_color(COLOR_GREY, lv.PART.MAIN)
                    self.tank_meter.set_style_arc_width(16, lv.PART.MAIN)
                    self.tank_meter.set_rotation(90)
                    self.tank_meter.set_value(0)
                    lbl_percent = lv.label(page)
                    lbl_percent.set_text("-- %")
                    lbl_percent.set_style_text_color(COLOR_WHITE, 0)
                    lbl_percent.set_style_text_font(lv.font_montserrat_32, 0)
                    lbl_percent.set_pos(70, 100)
                    self.labels[topic_name] = lbl_percent
                    lbl_title = lv.label(page)
                    lbl_title.set_text(topic_cfg["label"])
                    lbl_title.set_style_text_color(COLOR_ACCENT, 0)
                    lbl_title.set_style_text_font(lv.font_montserrat_16, 0)
                    lbl_title.set_pos(75, 40)
                else:
                    panel, lbl_val = create_round_panel(
                        page,
                        topic_cfg["label"],
                        "--",
                        topic_cfg.get("unit", ""),
                        color_val
                    )
                    panel.set_pos(20, y_offset)
                    self.labels[topic_name] = lbl_val
                    y_offset += 100
            self.pages.append(page)

    def update(self):
        for topic, label in self.labels.items():
            val = mqtt_data.get(topic, "--")
            if self.tank_meter and topic == "N/0/Tank/0/Level":
                label.set_text("{} %".format(val))
                try:
                    self.tank_meter.set_value(int(float(val)))
                except:
                    self.tank_meter.set_value(0)
            else:
                label.set_text(str(val))

    def show_page(self, idx):
        self.current = idx % len(self.pages)
        for i,p in enumerate(self.pages):
            if i == self.current:
                p.clear_flag(lv.obj.FLAG.HIDDEN)
            else:
                p.add_flag(lv.obj.FLAG.HIDDEN)

    def handle_swipe(self, e):
        dir = lv.indev_get_gesture_dir(lv.indev_get_act())
        if dir == lv.DIR.LEFT:
            self.show_page(self.current+1)
        elif dir == lv.DIR.RIGHT:
            self.show_page(self.current-1)

pages = DataPages()

# --- ERROR SCREEN ---
error_screen = None
retry_btn = None

def show_error(text):
    global error_screen, retry_btn
    if error_screen:
        error_screen.del_async()
    error_screen = lv.obj()
    error_screen.set_size(240,240)
    error_screen.set_style_bg_color(COLOR_BG, 0)
    lv.scr_load(error_screen)
    panel = lv.obj(error_screen)
    panel.set_size(200, 120)
    panel.set_pos(20, 40)
    panel.set_style_bg_color(COLOR_PANEL, 0)
    panel.set_style_radius(30, 0)
    lbl = lv.label(panel)
    lbl.set_text("Connection Error")
    lbl.set_style_text_color(COLOR_ORANGE, 0)
    lbl.set_style_text_font(lv.font_montserrat_18, 0)
    lbl.set_pos(30,20)
    lbl2 = lv.label(panel)
    lbl2.set_text(text)
    lbl2.set_style_text_color(COLOR_WHITE, 0)
    lbl2.set_pos(30,60)
    retry_btn = lv.btn(error_screen)
    retry_btn.set_size(120,40)
    retry_btn.set_pos(60,180)
    retry_btn.set_style_bg_color(COLOR_ACCENT, 0)
    btn_lbl = lv.label(retry_btn)
    btn_lbl.set_text("Try Again")
    btn_lbl.set_style_text_color(COLOR_WHITE, 0)
    retry_btn.add_event_cb(lambda e: try_connect(), lv.EVENT.CLICKED, None)

def try_connect():
    global client, mqtt_connected
    ok, err = connect_network()
    if not ok:
        show_error("Network: " + err)
        return
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
        client.set_callback(mqtt_callback)
        client.connect()
        for t in MQTT_TOPICS:
            client.subscribe(t["topic"])
        mqtt_connected = True
        lv.scr_load(pages.container)
    except Exception as e:
        mqtt_connected = False
        show_error("MQTT: " + str(e))

# --- MQTT CALLBACK ---
def mqtt_callback(topic, msg):
    topic_str = topic.decode() if isinstance(topic, bytes) else topic
    msg_str = msg.decode() if isinstance(msg, bytes) else msg
    if topic_str in mqtt_data:
        # Find topic config for formatting
        topic_cfg = next((t for t in MQTT_TOPICS if t["topic"] == topic_str), None)
        if topic_cfg:
            if "Soc" in topic_str or "Level" in topic_str:
                try:
                    mqtt_data[topic_str] = "{:.1f}".format(float(msg_str))
                except:
                    mqtt_data[topic_str] = msg_str
            elif "TimeToGo" in topic_str:
                # TimeToGo is typically seconds, convert to hours
                try:
                    sec = int(msg_str)
                    mqtt_data[topic_str] = "{:.2f}".format(sec/3600)
                except:
                    mqtt_data[topic_str] = msg_str
            else:
                mqtt_data[topic_str] = msg_str
            pages.update()

# --- MAIN LOOP ---
try_connect()
last_msg = time.time()
while True:
    try:
        if mqtt_connected:
            client.check_msg()
            # If no data for a while, show error
            if time.time()-last_msg > 30:
                show_error("No MQTT data received")
        lv.task_handler()
        time.sleep_ms(50)
    except OSError as e:
        mqtt_connected = False
        show_error("Network error: " + str(e))
        time.sleep(1)
    except Exception as e:
        mqtt_connected = False
        show_error("Other error: " + str(e))
        time.sleep(1)