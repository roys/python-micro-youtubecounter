import max7219
from machine import Pin, SPI
import time
import urequests
import network

WIFI_SSID = "FILL_IN_YOUR_WIFI_NETWORK_NAME"
WIFI_PASSWORD = "FILL_IN_YOUR_WIFI_PASSWORD"
YOUTUBE_API_KEY = "FILL_IN_YOUR_YOUTUBE_API_KEY"
YOUTUBE_CHANNEL_ID = "FILL_IN_YOUR_YOUTUBE_CHANNEL_ID"

MAX7219_NUM_OF_MODULES = 4
MAX7219_PIXELS_PER_MODULE = 8
MAX7219_TOTAL_WIDTH = MAX7219_NUM_OF_MODULES * MAX7219_PIXELS_PER_MODULE

display = None


def init_display():
    global display
    spi = SPI(1, baudrate=10000000, polarity=0, phase=0)
    cs = Pin(12, Pin.OUT)  # D6 of NodeMCU
    display = max7219.Matrix8x8(spi, cs, MAX7219_NUM_OF_MODULES)

    display.brightness(3)  # 0-15
    display.fill(0)  # Clear the display
    display.show()


def scroll_text(text, delay=0.05, scroll_off_screen=False):
    if scroll_off_screen:
        text += "    "
    width = len(text) * 8
    for pos in range(-MAX7219_TOTAL_WIDTH, width):
        display.fill(0)
        display.text(text, MAX7219_TOTAL_WIDTH - pos, 0, 1)
        display.show()
        time.sleep(delay)


def display_text(text):
    display.fill(0)
    display.text(text, 0, 0, 1)
    display.show()


def connect_wifi():
    try:
        access_point = network.WLAN(network.AP_IF)
        access_point.active(False)  # No need for an access point
        wlan = network.WLAN(network.STA_IF)
        # wlan.config(pm=network.WLAN.PM_POWERSAVE) # Makes the whole device go sluggish
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        scroll_text(WIFI_SSID, delay=0.03, scroll_off_screen=True)
        for _ in range(50):
            if wlan.isconnected():
                break
            time.sleep(0.1)

        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            scroll_text(ip)
        else:
            scroll_text(f"Could not connect to Wi-Fi. Restart.")
    except Exception as e:
        scroll_text(f"Error: {str(e)}.")


def print_sub_count():
    url = (
        "https://www.googleapis.com/youtube/v3/channels"
        "?part=statistics"
        f"&id={YOUTUBE_CHANNEL_ID}"
        f"&key={YOUTUBE_API_KEY}"
    )
    last_sub_count = None
    error_count = 0
    while True:
        try:
            status = None
            response = urequests.get(url)
            data = response.json()
            status = response.status_code
            # print(status)
            # print(data)
            # print(url)
            response.close()
            count = str(int(data["items"][0]["statistics"]["subscriberCount"]))
            error_count = 0
            if count != last_sub_count:
                last_sub_count = count
                while len(count) < 4:
                    count = " " + count
                scroll_text(count)
            time.sleep(60)
        except Exception as e:
            error_count += 1
            if error_count >= 10:
                scroll_text(f"Error: {status} - {str(e)}.")
                print(e)
                last_sub_count = None
            time.sleep(60)


init_display()
scroll_text("Starting...", scroll_off_screen=True)
connect_wifi()
print_sub_count()
