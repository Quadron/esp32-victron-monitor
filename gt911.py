import machine

class GT911:
    def __init__(self, i2c, int_pin=None):
        self.i2c = i2c
        self.addr = 0x5D
        self.int_pin = int_pin
        if self.int_pin:
            self.irq = machine.Pin(self.int_pin, machine.Pin.IN)
        # Quick presence check
        try:
            self.i2c.readfrom_mem(self.addr, 0x8140, 1)
        except Exception:
            print("GT911 touch not found!")

    def read(self):
        # Read touch data (only basic single touch)
        try:
            buf = self.i2c.readfrom_mem(self.addr, 0x814E, 8)
            touch_points = buf[0] & 0x0F
            if touch_points == 0:
                return None
            x = buf[1] | (buf[2] << 8)
            y = buf[3] | (buf[4] << 8)
            return (x, y)
        except Exception:
            return None