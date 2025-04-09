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

# Receiver MAC address
RECEIVER_MAC = b'\x94\x54\xc5\xa8\x42\x24'

# Add peer
e.add_peer(RECEIVER_MAC)

# Counter for message ID and last RSSI value
count = 0
last_rssi = "N/A"  # Store the last received RSSI
last_percentage = "N/A"  # Store signal percentage

# Function to convert RSSI to percentage
def rssi_to_percentage(rssi):
    try:
        rssi_val = int(rssi)
        # RSSI typically ranges from -30 (excellent) to -90 (poor)
        # Convert to percentage (higher is better)
        if rssi_val >= -50:
            return 100
        elif rssi_val <= -100:
            return 0
        else:
            # Linear scale from -50 (100%) to -100 (0%)
            return int(100 - ((abs(rssi_val) - 50) * 2))
    except:
        return "N/A"

# Function to check for any incoming messages and get RSSI
def check_for_rssi():
    global last_rssi, last_percentage
    # Non-blocking receive (timeout=0)
    host, msg = e.recv(0)
    if msg:  # If we got a message
        host_mac = ubinascii.hexlify(host).decode()
        try:
            # Try to parse RSSI from message if it's in our expected format
            if msg.startswith(b'RSSI:'):
                last_rssi = msg.decode().split(':')[1]
                last_percentage = rssi_to_percentage(last_rssi)
                print(f"Got RSSI feedback: {last_rssi} dBm ({last_percentage}%)")
        except Exception as ex:
            print(f"Error parsing RSSI: {ex}")
    return last_rssi, last_percentage

# Function to draw signal bars using pixel method instead of fill_rect
def draw_signal_bars(oled, x, y, percentage):
    if percentage == "N/A":
        oled.text("Signal: N/A", x, y)
        return
    
    # Draw text percentage
    oled.text(f"Sig: {percentage}%", x, y)
    
    # Draw visual signal indicator using individual pixels
    bar_x = x + 90
    bar_y = y
    
    # Draw 1-4 bars based on signal strength
    if percentage >= 75:
        bars = 4
    elif percentage >= 50:
        bars = 3
    elif percentage >= 25:
        bars = 2
    elif percentage > 0:
        bars = 1
    else:
        bars = 0
    
    for i in range(bars):
        # Draw bar using individual pixels
        bar_width = 3
        bar_height = i + 5  # Height increases with signal strength
        
        # Draw a solid bar by setting individual pixels
        for px in range(bar_width):
            for py in range(bar_height):
                oled.pixel(bar_x + (i*5) + px, bar_y + 8 - py, 1)

# Main loop to send data
while True:
    try:
        # Check for any incoming messages that might contain RSSI
        rssi_value, percentage = check_for_rssi()
        
        # Create and send message
        message = f"Hello #{count}"
        print(f"Sending: {message}")
        
        # Update OLED display
        oled.fill(0)
        oled.text("ESP-NOW Sender", 0, 0)
        oled.text("Sending:", 0, 16)
        oled.text(message, 0, 26)
        oled.text(f"Count: {count}", 0, 36)
        # Display RSSI as dBm and draw signal bars
        oled.text(f"RSSI: {rssi_value} dBm", 0, 56)
        draw_signal_bars(oled, 0, 46, percentage)
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
