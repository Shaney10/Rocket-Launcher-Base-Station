# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of sending and recieving data with the RFM95 LoRa radio.
# Author: Tony DiCola
import time
import board
import busio
import digitalio
from digitalio import DigitalInOut, Direction, Pull
import terminalio
import displayio
import adafruit_displayio_ssd1306
from adafruit_display_text import label
import adafruit_rfm9x

Switch_A = digitalio.DigitalInOut(board.D9)
Switch_C = digitalio.DigitalInOut(board.D5)

Switch_A.direction = digitalio.Direction.INPUT
Switch_C.direction = digitalio.Direction.INPUT

Switch_A.pull = Pull.UP
Switch_C.pull = Pull.UP

displayio.release_displays()
#Define I2C instance using the default SCL SDA pins
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3c)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)

# Make the display context
splash = displayio.Group()
display.show(splash)

color_bitmap = displayio.Bitmap(128, 32, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)
time.sleep(2.0)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(124, 30, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=2, y=1)
splash.append(inner_sprite)

# Draw a label
PowerOnText1 = "Hello Rocket"
PowerOnText2 = "Launch Version 1.0!"
text1_area = label.Label(terminalio.FONT, text=PowerOnText1, color=0xFFFF00, x=4, y=6)
splash.append(text1_area)
text2_area = label.Label(terminalio.FONT, text=PowerOnText2, color=0xFFFF00, x=4, y=22)
splash.append(text2_area)
time.sleep(5.0)

# Draw a label
NoneText = "Rocket Say Something!"
RecieveText = "Rocket Said Hello!"

# Define radio parameters.
RADIO_FREQ_MHZ = 915.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.

# Define pins connected to the chip, use these if wiring up the breakout according to the guide:
CS = digitalio.DigitalInOut(board.D10)
RESET = digitalio.DigitalInOut(board.D11)
# Or uncomment and instead use these if using a Feather M0 RFM9x board and the appropriate
# CircuitPython build:
# CS = digitalio.DigitalInOut(board.RFM9X_CS)
# RESET = digitalio.DigitalInOut(board.RFM9X_RST)

# Define the onboard LED
LED = digitalio.DigitalInOut(board.D13)
LED.direction = digitalio.Direction.OUTPUT

# Initialize SPI bus.
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Initialze RFM radio
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!

# You can however adjust the transmit power (in dB).  The default is 13 dB but
# high power radios like the RFM95 can go up to 23 dB:
rfm9x.tx_power = 23

# Send a packet.  Note you can only send a packet up to 252 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.
rfm9x.send(bytes("Hello world!\r\n", "utf-8"))
print("Sent Hello World message!")

# Wait to receive packets.  Note that this library can't receive data at a fast
# rate, in fact it can only receive and process one 252 byte packet at a time.
# This means you should only use this for low bandwidth scenarios, like sending
# and receiving a single message at a time.
print("Waiting for packets...")

while True:
    if Switch_A.value:
        print("Switch_A is High!")
        rfm9x.send(bytes("No Launch!\r\n", "utf-8"))
    else:
        print("Switch_A is Low!")
        rfm9x.send(bytes("Launch", "utf-8"))
        continue
    if Switch_C.value:
        print("Switch_C is High!")
    else:
        print("Switch_C is Low!")

    rfm9x.send(bytes("Hello Rocket!\r\n", "utf-8"))
    print("Sent Hello Rocket!")
    packet = rfm9x.receive()
    # Optionally change the receive timeout from its default of 0.5 seconds:
    # packet = rfm9x.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is None:
        # Packet has not been received
        LED.value = False
        print("Rocket Say Something! Listening again...")
        text1_area = label.Label(terminalio.FONT, text=NoneText, color=0xFFFF00, x=4, y=6)
        display.show(text1_area)
    else:

        # Received a packet!
        LED.value = True
        # Print out the raw bytes of the packet:
        print("Received (raw bytes): {0}".format(packet))
        # And decode to ASCII text and print it too.  Note that you always
        # receive raw bytes and need to convert to a text format like ASCII
        # if you intend to do string processing on your data.  Make sure the
        # sending side is sending ASCII data before you try to decode!
        packet_text = str(packet, "ascii")
        print("Received (ASCII): {0}".format(packet_text))
        # Also read the RSSI (signal strength) of the last received message and
        # print it.
        rssi = rfm9x.last_rssi
        print("Received signal strength: {0} dB".format(rssi))
        text1_area = label.Label(terminalio.FONT, text=RecieveText, color=0xFFFF00, x=4, y=6)
        display.show(text1_area)
        time.sleep(1.0)
        text2_area = label.Label(terminalio.FONT, text="Received: {0}".format(packet_text), color=0xFFFF00, x=4, y=22)
        display.show(text2_area)