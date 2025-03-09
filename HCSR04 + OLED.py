# Complete project details at https://RandomNerdTutorials.com/micropython-hc-sr04-ultrasonic-esp32-esp8266/
from hcsr04 import HCSR04
import ssd1306
from time import sleep
from machine import Pin, SoftI2C

# ESP32 Pin assignment
i2c = SoftI2C(scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# HCSR04
sensor = HCSR04(trigger_pin=18, echo_pin=5, echo_timeout_us=10000)

while True:
    distance = sensor.distance_cm()
    oled.fill(0)
    oled.text('Dist: %3.1f cm' %distance, 0, 0)
    oled.show()
    