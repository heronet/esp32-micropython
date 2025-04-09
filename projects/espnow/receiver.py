import network
import espnow
import ubinascii
import time
from machine import Pin, I2C
import ssd1306

# Initialize OLED display
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize WiFi in Station mode
sta = network.WLAN(network.STA_IF)
sta.active(True)

# Get MAC address
mac = ubinascii.hexlify(sta.config('mac')).decode()
formatted_mac = ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)])

# Display MAC address on OLED
oled.fill(0)
oled.text("ESP-NOW Receiver", 0, 0)
oled.text("MAC:", 0, 16)
oled.text(formatted_mac[:12], 0, 26)
oled.text(formatted_mac[12:], 0, 36)
oled.text("Waiting for msg...", 0, 54)
oled.show()

# Print MAC information to console (for setting up sender)
print(f"Receiver MAC address: {mac}")
print(f"Copy this for sender:")
print(f"RECEIVER_MAC = b'\\x" + '\\x'.join([mac[i:i+2] for i in range(0, len(mac), 2)]) + "'")

# Initialize ESP-NOW
e = espnow.ESPNow()
e.active(True)

# Count received messages
recv_count = 0

# Main loop to receive data
print("Waiting for messages...")
while True:
    host, msg = e.recv()
    if msg:  # Check if message is not empty
        recv_count += 1
        
        # Convert host (MAC) to readable format
        host_mac = ubinascii.hexlify(host).decode()
        print(f"Received from: {host_mac}")
        print(f"Message: {msg.decode()}")
        
        # Update OLED display
        oled.fill(0)
        oled.text("ESP-NOW Receiver", 0, 0)
        oled.text("Msg received:", 0, 16)
        oled.text(msg.decode(), 0, 26)
        oled.text(f"Total msgs: {recv_count}", 0, 46)
        oled.show()