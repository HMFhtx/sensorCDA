import time
import json
import RPi.GPIO as GPIO
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# AWS IoT Core configuration
host = "a3qw7ret33putt-ats.iot.us-east-1.amazonaws.com"  # Your IoT endpoint
port = 8883
rootCAPath = "AmazonRootCA1.pem"  
privateKeyPath = "bfc9084f5e0edb61af0a6c6d0897a1379e3ec791b87b3855d286e49f2c79eb45-private.pem.key"  
certificatePath = "bfc9084f5e0edb61af0a6c6d0897a1379e3ec791b87b3855d286e49f2c79eb45-certificate.pem.crt"  

clientId = "CDA_Device_SoilMoisture"
topic = "/cda/sensorDataSoil"

# Sensor ID
sensor_id = "Sensor_03"

# Initialize AWS IoT MQTT Client
client = AWSIoTMQTTClient(clientId)
client.configureEndpoint(host, port)
client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# MQTT Client Configurations
client.configureOfflinePublishQueueing(-1)  
client.configureDrainingFrequency(2)         
client.configureConnectDisconnectTimeout(10)  
client.configureMQTTOperationTimeout(5)       

# Connect to AWS IoT Core
print("Connecting to AWS IoT Core...")
client.connect()
print("Connected!")

# Setup Soil Moisture Sensor (Digital Output)
DO_PIN = 17  # GPIO17 (Pin 11)
GPIO.setmode(GPIO.BCM)
GPIO.setup(DO_PIN, GPIO.IN)

# Publish sensor data to AWS IoT
try:
    while True:
        # Read soil moisture (DO)
        soil_status = GPIO.input(DO_PIN)
        moisture_status = "Dry" if soil_status == 1 else "Moist"

        # Format timestamp as HH:MM
        timestamp = time.strftime("%H:%M")

        # Create JSON payload
        payload = json.dumps({
            "sensor_id": sensor_id,
            "moisture_status": moisture_status,
            "timestamp": timestamp
        })

        print(f"Publishing to AWS IoT: {payload}")
        client.publish(topic, payload, 1)

        time.sleep(3)  # Send data every 3 seconds

except KeyboardInterrupt:
    print("Interrupted, cleaning up...")
    GPIO.cleanup()
    client.disconnect()
    print("Disconnected from AWS IoT Core.")
