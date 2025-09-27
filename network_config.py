# network_config.py
# Handles network connection logic for both Ethernet (W5500) and WiFi (ESP32)

import network
import time
import machine
import ujson

# --- Ethernet (W5500) config ---
ETH_CS   = 47
ETH_SCK  = 36
ETH_MOSI = 35
ETH_MISO = 37

# --- WiFi config ---
try:
    with open('secrets.json', 'r') as f:
        secrets = ujson.load(f)
        WIFI_SSID = secrets['wifi_ssid']
        WIFI_PASSWORD = secrets['wifi_password']
except Exception as e:
    WIFI_SSID = None
    WIFI_PASSWORD = None

# --- Unified connect_network() ---
def connect_network():
    """
    Try Ethernet first. If not available or fails, try WiFi.
    Returns (True, "") on success, (False, reason) on failure.
    """
    # Try Ethernet
    try:
        from wiznet5k import WIZNET5K
        spi_eth = machine.SoftSPI(sck=machine.Pin(ETH_SCK), mosi=machine.Pin(ETH_MOSI), miso=machine.Pin(ETH_MISO))
        eth = WIZNET5K(spi_eth, machine.Pin(ETH_CS))
        eth.active(True)
        for _ in range(20):
            if eth.is_link_up():
                break
            time.sleep(0.2)
        else:
            raise Exception("Ethernet link not up")
        eth.ifconfig('dhcp')
        return True, "ethernet"
    except Exception as e:
        # Fallback to WiFi
        try:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            if not WIFI_SSID or not WIFI_PASSWORD:
                return False, "No WiFi credentials"
            if not wlan.isconnected():
                wlan.connect(WIFI_SSID, WIFI_PASSWORD)
                for _ in range(40):
                    if wlan.isconnected():
                        break
                    time.sleep(0.2)
                else:
                    return False, "WiFi not connected"
            return True, "wifi"
        except Exception as e2:
            return False, f"No network: Ethernet error: {e}, WiFi error: {e2}"
