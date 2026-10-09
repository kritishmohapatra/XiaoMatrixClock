from machine import Pin, SoftSPI
import max7219
import time
import network
import ntptime


# =========================
# WiFi
# =========================
SSID = "kritish"
PASSWORD = "@Krrs2069"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

print("Connecting WiFi...")

wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    time.sleep(1)

print("WiFi Connected:", wlan.ifconfig())


# =========================
# NTP SYNC
# =========================

# Try different NTP servers
ntp_servers = [
    "pool.ntp.org",
    "time.google.com",
    "time.cloudflare.com",
    "in.pool.ntp.org"
]

synced = False

for server in ntp_servers:

    try:
        print("Trying NTP:", server)

        ntptime.host = server

        ntptime.settime()

        print("NTP synced successfully!")
        print("UTC:", time.localtime())

        synced = True
        break

    except Exception as e:

        print("NTP failed:", e)
        time.sleep(2)


if not synced:
    print("WARNING: NTP synchronization failed!")
    print("Check your WiFi/router Internet access.")


# =========================
# MAX7219
# =========================

spi = SoftSPI(
    baudrate=500000,
    polarity=0,
    phase=0,
    sck=Pin(7),
    mosi=Pin(9),
    miso=Pin(8)
)

cs = Pin(2, Pin.OUT)

display = max7219.Matrix8x8(spi, cs, 4)

display.brightness(4)


# =========================
# FONT
# =========================

FONT = {
    0: (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    1: (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    2: (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    3: (0x1E, 0x01, 0x01, 0x0E, 0x01, 0x01, 0x1E),
    4: (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    5: (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    6: (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    7: (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    8: (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    9: (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
}


# =========================
# DRAW DIGIT
# =========================

def draw_digit(d, x, y=0):

    for r in range(7):

        row = FONT[d][r]

        for c in range(5):

            if row & (0x10 >> c):

                display.pixel(
                    x + c,
                    y + r,
                    1
                )


# =========================
# DRAW COLON
# =========================

def draw_colon(x, on=True):

    if on:

        for dx in (0, 1):

            for dy in (1, 2, 4, 5):

                display.pixel(
                    x + dx,
                    dy,
                    1
                )


# =========================
# IST
# =========================

IST_OFFSET = 5 * 3600 + 30 * 60


# =========================
# CLOCK
# =========================

while True:

    # Get UTC timestamp
    utc_time = time.time()

    # Convert UTC -> IST
    ist_time = utc_time + IST_OFFSET

    tm = time.localtime(ist_time)

    h = tm[3]
    m = tm[4]
    s = tm[5]

    print(
        "IST:",
        "{:02d}:{:02d}:{:02d}".format(
            h, m, s
        )
    )

    # Clear
    display.fill(0)

    # Hours
    draw_digit(h // 10, 2)
    draw_digit(h % 10, 8)

    # Colon
    draw_colon(
        15,
        s % 2 == 0
    )

    # Minutes
    draw_digit(m // 10, 19)
    draw_digit(m % 10, 25)

    display.show()

    time.sleep(1)
