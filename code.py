#MIT License

#Copyright (c) 2023 Trevor Beaton

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import time
import board
import digitalio
import adafruit_fancyled.adafruit_fancyled as fancy
import neopixel
from adafruit_motorkit import MotorKit

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet

from adafruit_bluefruit_connect.button_packet import ButtonPacket
from adafruit_bluefruit_connect.color_packet import ColorPacket

kit = MotorKit(i2c=board.I2C())

ble = BLERadio()
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)

FULL_THROTTLE = 1.0
THIRD_THROTTLE = 0.70
HALF_THROTTLE = 0.5
LOW_THROTTLE = 0.3

CURRENT_THROTTLE = 0.5


NUM_LEDS = 8  # change to reflect your LED strip
NEOPIXEL_PIN = board.D5  # change to reflect your wiring

# Palettes can have any number of elements in various formats
# check https://learn.adafruit.com/fancyled-library-for-circuitpython/colors
# for more info

# Declare a 6-element RGB rainbow palette
PALETTE_RAINBOW = [
    fancy.CRGB(1.0, 0.0, 0.0),  # Red
    fancy.CRGB(0.5, 0.5, 0.0),  # Yellow
    fancy.CRGB(0.0, 1.0, 0.0),  # Green
    fancy.CRGB(0.0, 0.5, 0.5),  # Cyan
    fancy.CRGB(0.0, 0.0, 1.0),  # Blue
    fancy.CRGB(0.5, 0.0, 0.5),
]  # Magenta

# Declare a Purple Gradient palette
PALETTE_GRADIENT = [
    fancy.CRGB(160, 0, 141),  # Purples
    fancy.CRGB(77, 0, 160),
    fancy.CRGB(124, 0, 255),
    fancy.CRGB(0, 68, 214),
]

# Declare a FIRE palette
PALETTE_FIRE = [
    fancy.CRGB(0, 0, 0),  # Black
    fancy.CHSV(1.0),  # Red
    fancy.CRGB(1.0, 1.0, 0.0),  # Yellow
    0xFFFFFF,
]  # White

# Declare a Water Colors palette
PALETTE_WATER = [
    fancy.CRGB(0, 214, 214),  # blues and cyans
    fancy.CRGB(0, 92, 160),
    fancy.CRGB(0, 123, 255),
    fancy.CRGB(0, 68, 214),
]


pixels = neopixel.NeoPixel(NEOPIXEL_PIN, NUM_LEDS, brightness=1.0, auto_write=False)

offset = 0  # Positional offset into color palette to get it to 'spin'
offset_increment = 1
OFFSET_MAX = 1000000


def set_palette(palette):
    for i in range(NUM_LEDS):
        # Load each pixel's color from the palette using an offset, run it
        # through the gamma function, pack RGB value and assign to pixel.
        color = fancy.palette_lookup(palette, (offset + i) / NUM_LEDS)
        color = fancy.gamma_adjust(color, brightness=0.25)
        pixels[i] = color.pack()
    pixels.show()


# set initial palette to run on startup
palette_choice = PALETTE_RAINBOW

# True if cycling a palette
cycling = True


def move_forward():
    print("move_forward")
    kit.motor4.throttle = CURRENT_THROTTLE
    kit.motor3.throttle = -CURRENT_THROTTLE


def move_backward():
    print("move_backward")
    kit.motor4.throttle = -CURRENT_THROTTLE
    kit.motor3.throttle = CURRENT_THROTTLE


def move_left():
    print("move_left")
    kit.motor4.throttle = CURRENT_THROTTLE
    kit.motor3.throttle = -CURRENT_THROTTLE / 1.2


def move_right():
    print("move_right")
    kit.motor4.throttle = CURRENT_THROTTLE / 1.2
    kit.motor3.throttle = -CURRENT_THROTTLE


def stop():
    kit.motor4.throttle = 0.0
    kit.motor3.throttle = 0.0


while True:
    print("WAITING...")
    # Advertise when not connected.
    ble.start_advertising(advertisement)
    while not ble.connected:
        pass

    # Connected
    ble.stop_advertising()
    print("CONNECTED")

    # Loop and read packets
    while ble.connected:
        # Keeping trying until a good packet is received
        try:
            packet = Packet.from_stream(uart_server)
        except ValueError:
            continue

        # Only handle button packets
        if isinstance(packet, ButtonPacket):
            if packet.pressed:
                if packet.button == ButtonPacket.UP:
                    move_forward()
                elif packet.button == ButtonPacket.DOWN:
                    move_backward()
                elif packet.button == ButtonPacket.LEFT:
                    move_left()
                elif packet.button == ButtonPacket.RIGHT:
                    move_right()
                elif packet.button == ButtonPacket.BUTTON_1:
                    print("FULL_THROTTLE")
                    CURRENT_THROTTLE = FULL_THROTTLE
                elif packet.button == ButtonPacket.BUTTON_2:
                    print("THIRD_THROTTLE")
                    CURRENT_THROTTLE = THIRD_THROTTLE
                elif packet.button == ButtonPacket.BUTTON_3:
                    print("HALF_THROTTLE")
                    CURRENT_THROTTLE = HALF_THROTTLE
                elif packet.button == ButtonPacket.BUTTON_4:
                    print("LOW_THROTTLE")
                    CURRENT_THROTTLE = LOW_THROTTLE
            elif not packet.pressed:
                stop()

        if isinstance(packet, ColorPacket):
            cycling = False
            # Set all the pixels to one color and stay there.
            pixels.fill(packet.color)
            pixels.show()
        elif isinstance(packet, ButtonPacket):
            cycling = True
            if packet.pressed:
                if packet.button == ButtonPacket.BUTTON_1:
                    palette_choice = PALETTE_RAINBOW
                    print("Sent")
                elif packet.button == ButtonPacket.BUTTON_2:
                    palette_choice = PALETTE_GRADIENT
                    print("Sent")
                elif packet.button == ButtonPacket.BUTTON_3:
                    palette_choice = PALETTE_FIRE
                    print("Sent")
                elif packet.button == ButtonPacket.BUTTON_4:
                    palette_choice = PALETTE_WATER
                    print("Sent")
                # change the speed of the animation by incrementing offset
                elif packet.button == ButtonPacket.UP:
                    offset_increment += 1
                elif packet.button == ButtonPacket.DOWN:
                    offset_increment -= 1

        if cycling:
            offset = (offset + offset_increment) % OFFSET_MAX
            set_palette(palette_choice)
    # Disconnected
    print("DISCONNECTED")
