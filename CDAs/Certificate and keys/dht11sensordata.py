import time
import json
import board
import adafruit_dht
import ssl
import paho.mqtt.client as mqtt
# Add warning suppression to avoid deprecation messages
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# HiveMQ Configuration
broker = "5b3009ec3ac740e9bca14abfc408b9b2.s1.eu.hivemq.cloud"  # HiveMQ Cloud broker address
port = 8883  # TLS port for MQTT
username = "RustyHive"  # Your HiveMQ username
password = "Jammerlap!234"  # Your HiveMQ password
topic = "sensorData"  # Topic where data will be published
# Sensor ID (change based on the sensor you're using)
sensor_id = "Sensor_02"

# MQTT Client Setup - Using compatible initialization
client = mqtt.Client(client_id="pythonPublisher", protocol=mqtt.MQTTv5)
client.username_pw_set(username, password)

# Set up SSL/TLS for secure connection
client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
client.tls_insecure_set(True)

# Callback function when connected
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print("Connected to HiveMQ Cloud!")
    else:
        print("Failed to connect, reason code:", reason_code)

client.on_connect = on_connect

# Connect to the HiveMQ broker
client.connect(broker, port, keepalive=60)

# Start the MQTT network loop in a separate thread
client.loop_start()

# Initialize the DHT11 sensor
dht_device = adafruit_dht.DHT11(board.D4, use_pulseio=False)

# Publish sensor data to HiveMQ
try:
    while True:
        try:
            # Read the sensor data
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            
            if humidity is not None and temperature is not None:
                # Get the current timestamp (HH:MM format)
                timestamp = time.strftime("%H:%M")
                
                # Prepare the JSON payload
                payload = json.dumps({
                    "sensor_id": sensor_id,
                    "temperature": f"{temperature:.1f}C",
                    "humidity": f"{humidity:.1f}%",
                    "timestamp": timestamp
                })
                
                # Print and publish the message
                print(f"Publishing to HiveMQ: {payload}")
                client.publish(topic, payload, qos=1)
            else:
                print("Sensor error: No data received")
                
        except RuntimeError as error:
            print(f"Error reading sensor: {error}")
            
        # Send data every 3 seconds
        time.sleep(3)
        
except KeyboardInterrupt:
    print("Interrupted, cleaning up...")
    dht_device.exit()
    client.loop_stop()  # Stop the network loop
    client.disconnect()  # Disconnect from HiveMQ
    print("Disconnected from HiveMQ Cloud.")