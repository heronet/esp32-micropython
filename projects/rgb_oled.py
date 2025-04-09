import ssd1306
from time import sleep
from machine import Pin, SoftI2C
import neopixel

# ESP32 Pin assignment
i2c = SoftI2C(scl=Pin(0), sda=Pin(9))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# NeoPixel setup
pixel_pin = Pin(8, Pin.OUT)   # NeoPixel connected to GPIO8
num_pixels = 1                # Number of NeoPixels (just one in this case)
np = neopixel.NeoPixel(pixel_pin, num_pixels)

# Set initial brightness (0.0 to 1.0)
brightness = 0.5

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def apply_brightness(color, brightness_value):
    """Apply brightness to RGB color."""
    r, g, b = color
    return (int(r * brightness_value), int(g * brightness_value), int(b * brightness_value))

position = 0
while True:
    # Calculate rainbow color
    original_color = wheel(position)
    
    # Apply brightness
    display_color = original_color  # Save original color for display
    adjusted_color = apply_brightness(original_color, brightness)
    
    # Update NeoPixel
    np[0] = adjusted_color
    np.write()
    
    # Update OLED display - show the ORIGINAL color values
    # This ensures the display shows the full color cycle at any brightness
    r, g, b = display_color
    oled.fill(0)
    oled.text('Hello ESP32-C6', 0, 0)
    oled.text('Rainbow LED:', 0, 16)
    oled.text(f'R:{r} G:{g} B:{b}', 0, 32)
    oled.text(f'Brightness: {int(brightness*100)}%', 0, 48)
    oled.show()
    
    # Move to next color position - always increment at full speed
    position = (position + 1) % 256
    sleep(0.05)  # Consistent speed regardless of brightness
