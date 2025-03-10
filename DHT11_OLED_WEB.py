from machine import Pin, SoftI2C
import ssd1306
from time import sleep
import dht
import network
import socket

# OLED Pin assignment
i2c = SoftI2C(scl=Pin(21), sda=Pin(22))

oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

sensor = dht.DHT11(Pin(5))

# Function to connect to Wi-Fi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)  # Deactivate first
    sleep(1)
    wlan.active(True)   # Reactivate
    sleep(1)
    
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect('CAMPHIGH', 'samcam69')  # Replace with your Wi-Fi credentials
        
        # Wait for connection
        for _ in range(10):  # Try for 10 seconds
            if wlan.isconnected():
                break
            sleep(1)
    
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("Connected to Wi-Fi. IP:", ip)
        return ip
    else:
        print("Failed to connect to Wi-Fi")
        return None

# Connect to Wi-Fi
ip = connect_to_wifi()

# Display the IP address on the OLED
if ip:
    oled.fill(0)
    oled.text("ESP32-WROOM-32", 0, 0)
    oled.text("Micropython", 0, 10)
    oled.text("IP:", 0, 20)
    oled.text(ip, 0, 30)
    oled.show()
else:
    oled.fill(0)
    oled.text("ESP32-WROOM-32", 0, 0)
    oled.text("Micropython", 0, 10)
    oled.text("Wi-Fi Failed", 0, 20)
    oled.show()

# Function to read sensor data
def get_sensor_data():
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    temp_f = temp * (9/5) + 32.0
    return temp, temp_f, hum

# Simple HTTP server
def start_http_server(ip):
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    sock = socket.socket()
    sock.bind(addr)
    sock.listen(1)
    print("HTTP server started on http://{}:80".format(ip))
    
    while True:
        try:
            client, addr = sock.accept()
            print("Client connected from:", addr)
            
            # Read sensor data
            temp, temp_f, hum = get_sensor_data()
            
            # Create HTTP response
            response = """HTTP/1.1 200 OK
Content-Type: text/html

<html>
    <head>
        <meta http-equiv="refresh" content="1">
        <title>ESP32 DHT11 Sensor</title>
    </head>
    <body>
        <h1>ESP32 DHT11 Sensor</h1>
        <p>Temperature: {:.1f} °C</p>
        <p>Temperature: {:.1f} °F</p>
        <p>Humidity: {:.1f} %</p>
    </body>
</html>
""".format(temp, temp_f, hum)
            
            # Send response to client
            client.send(response)
            client.close()
            print("Response sent to client")
        except Exception as e:
            print("Error:", e)
            client.close()

# Update OLED display
def update_display():
    temp, temp_f, hum = get_sensor_data()
    oled.fill(0)
    oled.text("ESP32-WROOM-32", 0, 0)
    oled.text("Micropython", 0, 10)
    oled.text('Temp 1: %3.1f C' % temp, 0, 30)
    oled.text('Temp 2: %3.1f F' % temp_f, 0, 40)
    oled.text('Humidity: %3.1f %%' % hum, 0, 50)
    oled.show()

# Main loop
if ip:
    start_http_server(ip)  # Start the HTTP server
else:
    print("Web server not started due to Wi-Fi failure.")
    while True:
        try:
            update_display()
            sleep(1)
        except OSError as e:
            oled.fill(0)
            oled.text("ESP32-WROOM-32", 0, 0)
            oled.text("Micropython", 0, 10)
            oled.text('Failed to read sensor.', 0, 30)
            oled.show()
