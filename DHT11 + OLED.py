# Complete project details at https://RandomNerdTutorials.com/micropython-ssd1306-oled-scroll-shapes-esp32-esp8266/

from machine import Pin, SoftI2C
import ssd1306
from time import sleep
import gfx
import dht

# ESP32 Pin assignment
i2c = SoftI2C(scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

sensor = dht.DHT11(Pin(5))

while True:
  try:
    oled.fill(0)
      
    sleep(1)
    
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    temp_f = temp * (9/5) + 32.0
    print('Temperature: %3.1f C' %temp)
    print('Temperature: %3.1f F' %temp_f)
    print('Humidity: %3.1f %%' %hum)
    
    oled.text('Temp: %3.1f C' %temp, 0, 0)
    oled.text('Temp: %3.1f F' %temp_f, 0, 10)
    oled.text('Humidity: %3.1f %%' %hum, 0, 20)
    
    oled.show()

  except OSError as e:
    print('Failed to read sensor.')



