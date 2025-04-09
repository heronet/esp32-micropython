import ssd1306
from time import sleep
from machine import Pin, SoftI2C
import neopixel
import network
import socket
import time
import json

# ESP32 Pin assignment
i2c = SoftI2C(scl=Pin(0), sda=Pin(9))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# NeoPixel setup
pixel_pin = Pin(8, Pin.OUT)   # NeoPixel connected to GPIO8
num_pixels = 1                # Number of NeoPixels (just one in this case)
np = neopixel.NeoPixel(pixel_pin, num_pixels)

# Parameters for LED control - can be modified via web interface
settings = {
    'brightness': 0.5,        # 0.0 to 1.0
    'speed': 0.05,            # Delay in seconds
    'rainbow_enable': True,   # Enable rainbow animation
    'static_color': (128, 128, 128)  # Default static color if not in rainbow mode
}

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

# Set up WiFi Access Point
def setup_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid='ESP32-NeoPixel', password='12345678')
    
    while not ap.active():
        pass
        
    print('AP Mode Active')
    print('IP Address:', ap.ifconfig()[0])
    return ap.ifconfig()[0]

# Alternative: Connect to existing WiFi network
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(ssid, password)
        
        # Wait for connection with timeout
        max_wait = 10
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(1)
            
        if wlan.isconnected():
            print('Connected to WiFi')
            print('IP Address:', wlan.ifconfig()[0])
            return wlan.ifconfig()[0]
        else:
            print('Failed to connect to WiFi')
            return None
    else:
        print('Already connected to WiFi')
        print('IP Address:', wlan.ifconfig()[0])
        return wlan.ifconfig()[0]

# HTML content
def get_html():
    brightness_val = int(settings['brightness']*100)
    speed_val = int(100-(settings['speed']*1000))
    r, g, b = settings['static_color']
    color_hex = "#{:02x}{:02x}{:02x}".format(r, g, b)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 NeoPixel Control</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial; text-align: center; margin: 20px; }
            .slider { width: 80%; margin: 20px auto; }
            .btn { background-color: #4CAF50; color: white; padding: 10px 20px; 
                   border: none; cursor: pointer; margin: 5px; border-radius: 4px; }
            .color-picker { margin: 20px auto; }
            .card { background-color: #f1f1f1; border-radius: 10px; 
                    padding: 20px; margin: 20px auto; max-width: 600px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>ESP32 NeoPixel Control</h1>
            
            <h2>Brightness</h2>
            <input type="range" min="0" max="100" value="BRIGHTNESS_VAL" class="slider" id="brightnessSlider">
            <p id="brightnessValue">BRIGHTNESS_VAL%</p>
            
            <h2>Speed</h2>
            <input type="range" min="1" max="100" value="SPEED_VAL" class="slider" id="speedSlider">
            <p id="speedValue">SPEED_VAL</p>
            
            <h2>Mode</h2>
            <button class="btn" id="rainbowBtn">Rainbow Mode</button>
            <button class="btn" id="staticBtn">Static Color</button>
            
            <h2>Static Color</h2>
            <input type="color" id="colorPicker" class="color-picker" value="COLOR_HEX">
            
            <div id="status" style="margin-top: 20px; color: green;"></div>
        </div>
        
        <script>
            // Function to send data to server
            function updateSettings(data) {
                fetch('/update', {
                    method: 'POST',
                    body: JSON.stringify(data),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.text())
                .then(data => {
                    document.getElementById('status').textContent = 'Updated!';
                    setTimeout(() => document.getElementById('status').textContent = '', 1000);
                });
            }
            
            // Brightness slider
            const brightnessSlider = document.getElementById('brightnessSlider');
            const brightnessValue = document.getElementById('brightnessValue');
            brightnessSlider.oninput = function() {
                brightnessValue.textContent = this.value + '%';
                updateSettings({brightness: this.value / 100});
            }
            
            // Speed slider
            const speedSlider = document.getElementById('speedSlider');
            const speedValue = document.getElementById('speedValue');
            speedSlider.oninput = function() {
                speedValue.textContent = this.value;
                updateSettings({speed: (100 - this.value) / 1000});
            }
            
            // Mode buttons
            document.getElementById('rainbowBtn').onclick = function() {
                updateSettings({rainbow_enable: true});
            }
            
            document.getElementById('staticBtn').onclick = function() {
                updateSettings({rainbow_enable: false});
                // Also send current color picker value
                const color = document.getElementById('colorPicker').value;
                const r = parseInt(color.substr(1,2), 16);
                const g = parseInt(color.substr(3,2), 16);
                const b = parseInt(color.substr(5,2), 16);
                updateSettings({static_color: [r, g, b]});
            }
            
            // Color picker
            document.getElementById('colorPicker').onchange = function() {
                const color = this.value;
                const r = parseInt(color.substr(1,2), 16);
                const g = parseInt(color.substr(3,2), 16);
                const b = parseInt(color.substr(5,2), 16);
                updateSettings({static_color: [r, g, b]});
            }
        </script>
    </body>
    </html>
    """
    
    # Replace placeholder values with actual values
    html = html.replace("BRIGHTNESS_VAL", str(brightness_val))
    html = html.replace("SPEED_VAL", str(speed_val))
    html = html.replace("COLOR_HEX", color_hex)
    
    return html

# Web server
def start_server(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    
    while True:
        try:
            conn, addr = s.accept()
            print('Client connected from', addr)
            request = conn.recv(1024)
            request = str(request)
            
            # Process POST request - update settings
            if 'POST /update' in request:
                # Find JSON payload
                json_start = request.find('{')
                json_end = request.rfind('}') + 1
                if json_start > 0 and json_end > 0:
                    try:
                        data_str = request[json_start:json_end]
                        data = json.loads(data_str)
                        print("Received data:", data)
                        
                        # Update settings
                        for key, value in data.items():
                            if key in settings:
                                settings[key] = value
                        
                        response = "Settings updated"
                    except Exception as e:
                        print("JSON parse error:", e)
                        response = "Error parsing settings"
                else:
                    response = "No data received"
                
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/plain\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)
                conn.close()
            
            # Serve HTML page for GET request
            else:
                response = get_html()
                conn.send('HTTP/1.1 200 OK\n')
                conn.send('Content-Type: text/html\n')
                conn.send('Connection: close\n\n')
                conn.sendall(response)
                conn.close()
        
        except Exception as e:
            print("Server error:", e)
            conn.close()
            # Don't break the loop, keep server running

# Start the web server in a separate thread
import _thread

# Choose one of these options:
# ip = setup_ap()  # Create access point
# OR
ip = connect_wifi("Sony Xperia 1 III", "00000000")  # Connect to existing WiFi

if ip:
    _thread.start_new_thread(start_server, (ip,))
    print(f"Web server started at http://{ip}")
else:
    print("Network connection failed")

# Display startup message on OLED
oled.fill(0)
oled.text('ESP32-C6 Server', 0, 0)
oled.text(f'{ip}', 0, 16)
oled.text('Connect to WiFi:', 0, 32)
oled.text('ESP32-NeoPixel', 0, 48)
oled.show()
sleep(5)  # Show IP for 5 seconds

# Main loop
position = 0
while True:
    if settings['rainbow_enable']:
        # Rainbow mode
        original_color = wheel(position)
        display_color = original_color
        position = (position + 1) % 256
    else:
        # Static color mode
        original_color = settings['static_color']
        display_color = original_color
    
    # Apply brightness
    adjusted_color = apply_brightness(original_color, settings['brightness'])
    
    # Update NeoPixel
    np[0] = adjusted_color
    np.write()
    
    # Update OLED display
    r, g, b = display_color
    oled.fill(0)
    oled.text(f'{ip}', 0, 0)
    oled.text(f'R:{r} G:{g} B:{b}', 0, 16)
    oled.text(f'Bright: {int(settings["brightness"]*100)}%', 0, 32)
    mode = "Rainbow" if settings['rainbow_enable'] else "Static"
    oled.text(f'Mode: {mode}', 0, 48)
    oled.show()
    
    # Use the speed setting from web interface
    sleep(settings['speed'])