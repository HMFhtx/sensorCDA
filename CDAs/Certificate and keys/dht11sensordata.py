import time
import json
import board
import adafruit_dht
import RPi.GPIO as GPIO
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# AWS IoT Core configuration
host = "a3qw7ret33putt-ats.iot.us-east-1.amazonaws.com"  # Your IoT endpoint
port = 8883
rootCAPath = "AmazonRootCA1.pem"  
privateKeyPath = "bfc9084f5e0edb61af0a6c6d0897a1379e3ec791b87b3855d286e49f2c79eb45-private.pem.key"  
certificatePath = "bfc9084f5e0edb61af0a6c6d0897a1379e3ec791b87b3855d286e49f2c79eb45-certificate.pem.crt"  

clientId = "CDA_Device_Dht11"
topic = "/cda/sensorDataDh11s"

#sensorID
sensor_id = "Sensor_02" #change this depending on which sensor id it is 

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

#Initialize DHT11 sensor
dht_device = adafruit_dht.DHT11(board.D4)

#Publish sensor data to AWS IoT
try:
    while True:
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity

            if humidity is not None and temperature is not None:
                # Format timestamp as HH:MM
                timestamp = time.strftime("%H:%M")

#Create JSON payload
                payload = json.dumps({
                    "sensor_id": sensor_id,
                    "temperature": f"{temperature:.1f}C",
                    "humidity": f"{humidity:.1f}%",
                    "timestamp": timestamp
                })

                print(f"Publishing to AWS IoT: {payload}")
                client.publish(topic, payload, 1)

            else:
                print("Sensor error: No data received")

        except RuntimeError as error:
            print(f"Error reading sensor: {error}")

        time.sleep(3)  # Send data every 3 seconds

except KeyboardInterrupt:
    print("Interrupted, cleaning up...")
    dht_device.exit()
    client.disconnect()
    print("Disconnected from AWS IoT Core.")