import network
import socket
import time
import _thread
from machine import Pin
from neopixel import NeoPixel

# NeoPixel setup
np = NeoPixel(Pin(8), 1)
current_color = (0, 0, 0)
rainbow_active = False
current_brightness = 255  # Default to full brightness

# WiFi credentials
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

def set_color(r, g, b):
    global current_color, rainbow_active
    rainbow_active = False
    current_color = (r, g, b)
    np[0] = current_color
    np.write()

def wheel(pos, brightness=255):
    """Generate rainbow colors across 0-255 positions with brightness control"""
    # Get base color
    if pos < 85:
        r, g, b = pos * 3, 255 - pos * 3, 0
    elif pos < 170:
        pos -= 85
        r, g, b = 255 - pos * 3, 0, pos * 3
    else:
        pos -= 170
        r, g, b = 0, pos * 3, 255 - pos * 3
    
    # Apply brightness factor
    brightness_factor = brightness / 255.0
    return (int(r * brightness_factor), 
            int(g * brightness_factor), 
            int(b * brightness_factor))

def infinite_rainbow():
    global rainbow_active, current_brightness
    pos = 0
    while True:
        if rainbow_active:
            # Use the wheel function with current brightness
            r, g, b = wheel(pos, current_brightness)
            np[0] = (r, g, b)
            np.write()
            pos = (pos + 1) % 256
            time.sleep_ms(20)
        else:
            time.sleep(0.1)

# Start rainbow thread
_thread.start_new_thread(infinite_rainbow, ())

# HTML page (updated with new controls)
html = """<!DOCTYPE html>
<html>
<head>
<title>RGB LED Control</title>
<style>
body {font-family: Arial; text-align: center; margin-top: 50px;}
.color-picker {margin: 20px;}
.slider {width: 80%; margin: 10px;}
button {padding: 10px 20px; font-size: 16px; margin: 5px;}
.rainbow-btn {background: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet); color: white;}
</style>
</head>
<body>
<h1>RGB LED Control</h1>
<div class="color-picker">
    <input type="color" id="color" name="color" value="#ff0000">
</div>
<div>
    <input type="range" min="0" max="255" value="255" class="slider" id="brightness">
    <p>Brightness: <span id="brightnessValue">100</span>%</p>
</div>
<button onclick="setColor()">Set Color</button>
<button onclick="off()">Turn Off</button>
<br><br>
<h2>Presets</h2>
<button onclick="preset('ff0000')">Red</button>
<button onclick="preset('00ff00')">Green</button>
<button onclick="preset('0000ff')">Blue</button>
<button onclick="preset('ffffff')">White</button>
<button class="rainbow-btn" onclick="startRainbow()">Infinite Rainbow</button>

<script>
function setColor() {
    var color = document.getElementById("color").value.substring(1);
    var brightness = document.getElementById("brightness").value;
    fetch("/color?value=" + color + "&brightness=" + brightness);
}

function off() {
    fetch("/off");
}

function preset(color) {
    document.getElementById("color").value = "#" + color;
    setColor();
}

function startRainbow() {
    var brightness = document.getElementById("brightness").value;
    fetch("/rainbow?brightness=" + brightness);
}

// Update brightness display
document.getElementById("brightness").oninput = function() {
    document.getElementById("brightnessValue").innerHTML = Math.round(this.value/255*100);
}
</script>
</body>
</html>
"""

def set_color_from_hex(hex_color, brightness=255):
    """Convert hex color (RRGGBB) to NeoPixel values"""
    global rainbow_active, current_brightness
    rainbow_active = False
    current_brightness = brightness
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Apply brightness (0-255 to 0-1.0)
    brightness_factor = brightness / 255.0
    set_color(
        int(r * brightness_factor),
        int(g * brightness_factor),
        int(b * brightness_factor)
    )

def connect_wifi():
    """Connect to WiFi"""
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Connecting to WiFi...")
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        while not sta_if.isconnected():
            time.sleep(0.5)
    print("Connected! IP address:", sta_if.ifconfig()[0])

def start_server():
    """Start the web server"""
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print("Listening on", addr)

    while True:
        conn, addr = s.accept()
        print("Client connected from", addr)
        request = conn.recv(1024)
        request = str(request)
        
        try:
            # Handle requests
            if "/color?value=" in request:
                hex_start = request.find("value=") + 6
                hex_end = request.find("&", hex_start)
                hex_color = request[hex_start:hex_start+6] if hex_end == -1 else request[hex_start:hex_end]
                
                bright_start = request.find("brightness=") + 11
                brightness = int(request[bright_start:bright_start+3].split(" ")[0].split("\\")[0])
                
                set_color_from_hex(hex_color, brightness)
                
            elif "/off" in request:
                set_color(0, 0, 0)
                
            elif "/rainbow" in request:
                global rainbow_active, current_brightness
                rainbow_active = True
                
                # Extract brightness if provided
                if "brightness=" in request:
                    bright_start = request.find("brightness=") + 11
                    current_brightness = int(request[bright_start:bright_start+3].split(" ")[0].split("\\")[0])
                
            # Send HTML response
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.send(html)
            
        except Exception as e:
            print("Error:", e)
            conn.send("HTTP/1.1 500 Internal Server Error\r\n\r\n")
            
        finally:
            conn.close()

# Main execution
try:
    connect_wifi()
    start_server()
except:
    set_color(0, 0, 0)
    print("Server stopped")
