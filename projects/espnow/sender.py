import network
import espnow
import time
import ubinascii
from machine import Pin, I2C
import ssd1306

# Initialize OLED display
i2c = I2C(0, scl=Pin(0), sda=Pin(9))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize WiFi in Station mode
sta = network.WLAN(network.STA_IF)
sta.active(True)

# Display MAC address on OLED
mac = ubinascii.hexlify(sta.config('mac')).decode()
formatted_mac = ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)])
oled.fill(0)
oled.text("ESP-NOW Sender", 0, 0)
oled.text("MAC:", 0, 16)
oled.text(formatted_mac[:12], 0, 26)
oled.text(formatted_mac[12:], 0, 36)
oled.show()
time.sleep(2)

# Initialize ESP-NOW
e = espnow.ESPNow()
e.active(True)

# Receiver MAC address converted to bytes format
# MAC: 94:54:c5:a8:42:24
RECEIVER_MAC = b'\x94\x54\xc5\xa8\x42\x24'

# Add peer
e.add_peer(RECEIVER_MAC)

# Counter for message ID
count = 0

# Main loop to send data
while True:
    try:
        message = f"Hello #{count}"
        print(f"Sending: {message}")
        
        # Update OLED display
        oled.fill(0)
        oled.text("ESP-NOW Sender", 0, 0)
        oled.text("Sending:", 0, 16)
        oled.text(message, 0, 26)
        oled.text(f"Count: {count}", 0, 46)
        oled.show()
        
        # Send message
        e.send(RECEIVER_MAC, message)
        count += 1
        time.sleep(2)  # Send every 2 seconds
    except Exception as e:
        print(f"Error: {e}")
        
        # Show error on OLED
        oled.fill(0)
        oled.text("ESP-NOW Sender", 0, 0)
        oled.text("Error sending!", 0, 16)
        oled.text(str(e)[:16], 0, 26)
        oled.text(str(e)[16:32], 0, 36)
        oled.show()
        
        time.sleep(1)