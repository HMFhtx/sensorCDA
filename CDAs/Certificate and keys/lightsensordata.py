import time
import json
import RPi.GPIO as GPIO
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# GPIO setup
GPIO.setmode(GPIO.BCM)
sensor_pin = 4  # Digital output pin from the sensor
GPIO.setup(sensor_pin, GPIO.IN)

# AWS IoT Core configuration
host = "a3qw7ret33putt-ats.iot.us-east-1.amazonaws.com"  # Your IoT endpoint
port = 8883
rootCAPath = "AmazonRootCA1.pem"  
privateKeyPath = "bfc9084f5e0edb61af0a6c6d0897a1379e3ec791b87b3855d286e49f2c79eb45-private.pem.key"  
certificatePath = "bfc9084f5e0edb61af0a6c6d0897a1379e3ec791b87b3855d286e49f2c79eb45-certificate.pem.crt"  

clientId = "CDA_Device_Lightsensor"
topic = "/cda/sensorDataLight"

#sensorID
sensor_id = "Sensor_01" #change this depending on which sensor id it is 

#Time format right here babyyy
timestamp = time.strftime("%H:%M")

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

# Function to read the sensor value
def read_sensor():
    return GPIO.input(sensor_pin)  # Returns HIGH (1) for darkness, LOW (0) for light

# Publish sensor data to AWS IoT
try:
    while True:
        sensor_value = read_sensor()
        status = "plant is in the dark" if sensor_value == GPIO.HIGH else "Plant is in direct sunlight"
        

        # Create JSON payload
        payload = json.dumps({
            "sensor_value": status,
            "timestamp": timestamp,
            "sensor_id" : sensor_id
        })

        print(f"Publishing to AWS IoT: {payload}")
        client.publish(topic, payload, 1)

        time.sleep(1)  # Send data every 5 seconds

except KeyboardInterrupt:
    print("Interrupted, cleaning up...")
    GPIO.cleanup()
    client.disconnect()
    print("Disconnected from AWS IoT Core.")