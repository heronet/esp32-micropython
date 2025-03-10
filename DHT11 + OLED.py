from machine import Pin, SoftI2C
import ssd1306
from time import sleep
import dht

# OLED Pin assignment
i2c = SoftI2C(scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

sensor = dht.DHT11(Pin(5))

while True:
  try:
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    temp_f = temp * (9/5) + 32.0
    
    print('Temperature: %3.1f C' %temp)
    print('Temperature: %3.1f F' %temp_f)
    print('Humidity: %3.1f %%' %hum)
    
    oled.fill(0)
    oled.text("ESP32-WROOM-32", 0, 0)
    oled.text("Micropython", 0, 10)
    
    oled.text('Temp 1: %3.1f C' %temp, 0, 30)
    oled.text('Temp 2: %3.1f F' %temp_f, 0, 40)
    oled.text('Humidity: %3.1f %%' %hum, 0, 50)
    
    oled.show()
    sleep(1)
  except OSError as e:
    oled.text("ESP32-WROOM-32", 0, 0)
    oled.text("Micropython", 0, 10)
    oled.text('Failed to read sensor.', 0, 30)