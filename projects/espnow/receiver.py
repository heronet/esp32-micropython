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

# Print MAC information to console
print(f"Receiver MAC address: {mac}")
print(f"Copy this for sender:")
print(f"RECEIVER_MAC = b'\\x" + '\\x'.join([mac[i:i+2] for i in range(0, len(mac), 2)]) + "'")

# Initialize ESP-NOW
e = espnow.ESPNow()
e.active(True)

# Count received messages
recv_count = 0
last_rssi = 0
last_sender = None

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

# Main loop to receive data
print("Waiting for messages...")
while True:
    # Try to use irecv if available (returns rssi directly in some versions)
    try:
        host, msg, rssi = e.irecv(0)
    except:
        # Fall back to standard recv
        host, msg = e.recv(0)
        rssi = None
    
    if msg:  # Check if message is not empty
        recv_count += 1
        
        # If rssi not provided by irecv, try to get it from peers_table
        if rssi is None:
            try:
                rssi = e.peers_table[host][0] if host in e.peers_table else "N/A"
            except:
                rssi = "N/A"
        
        # Calculate signal percentage
        percentage = rssi_to_percentage(rssi)
        
        # If this is our first message from this sender, add them as a peer
        if last_sender is None:
            try:
                e.add_peer(host)
                last_sender = host
            except:
                pass
        
        # Convert host (MAC) to readable format
        host_mac = ubinascii.hexlify(host).decode()
        print(f"Received from: {host_mac}")
        print(f"Message: {msg.decode()}")
        print(f"RSSI: {rssi} dBm ({percentage}%)")
        
        # Update OLED display
        oled.fill(0)
        oled.text("ESP-NOW Receiver", 0, 0)
        oled.text("Msg received:", 0, 10)
        oled.text(msg.decode(), 0, 20)
        oled.text(f"Count: {recv_count}", 0, 30)
        oled.text(f"RSSI: {rssi} dBm", 0, 50)
        draw_signal_bars(oled, 0, 40, percentage)
        oled.show()
        
        # Send RSSI back to sender if we've added them as peer
        if last_sender is not None:
            try:
                rssi_msg = f"RSSI:{rssi}"
                e.send(last_sender, rssi_msg)
            except:
                pass
        
        # Small delay to avoid overloading
        time.sleep(0.1)
