import time
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Simulated sensor reading function.
def read_sensor():
    # Replace this with your actual sensor reading logic
    # For example, if you're reading a temperature sensor, return the temperature value.
    return 23.5

# AWS IoT Core configuration (update these values with your own)
host = "a3qw7ret33putt-ats.iot.us-east-1.amazonaws.com"  # Your IoT endpoint
port = 8883
rootCAPath = "AmazonRootCA1.pem"                   # Path to your root CA certificate
privateKeyPath = "bfc9084f5e0edb61af0a6c6d0897a1379e3ec791b87b3855d286e49f2c79eb45-private.pem.key"       # Path to your CDA device's private key
certificatePath = "bfc9084f5e0edb61af0a6c6d0897a1379e3ec791b87b3855d286e49f2c79eb45-certificate.pem.crt"  # Path to your CDA device's certificate

clientId = "CDA_Device"
topic = "/cda/sensorData"  # Topic where sensor data will be published

# Initialize the AWS IoT MQTT Client
client = AWSIoTMQTTClient(clientId)
client.configureEndpoint(host, port)
client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# Optional configurations for robust behavior
client.configureOfflinePublishQueueing(-1)  # Infinite offline queueing
client.configureDrainingFrequency(2)          # Draining: 2 Hz
client.configureConnectDisconnectTimeout(10)  # 10 seconds timeout
client.configureMQTTOperationTimeout(5)         # 5 seconds timeout

# Connect to AWS IoT Core
print("Connecting to AWS IoT Core...")
client.connect()
print("Connected!")

# Publish sensor data at regular intervals
try:
    while True:
        # Read sensor value
        sensor_value = read_sensor()
        
        # Create a JSON payload with sensor data and a timestamp
        payload = json.dumps({
            "sensor_value": sensor_value,
            "timestamp": int(time.time())
        })
        print(f"Publishing sensor data to topic '{topic}': {payload}")
        
        # Publish the payload to the topic
        client.publish(topic, payload, 1)
        
        # Wait for 10 seconds before sending the next reading
        time.sleep(10)
except KeyboardInterrupt:
    print("Interrupted by user, disconnecting...")
    client.disconnect()
    print("Disconnected from AWS IoT Core.")
