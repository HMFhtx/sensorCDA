import time
import json
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# AWS IoT Core configuration
host = "a3qw7ret33putt-ats.iot.us-east-1.amazonaws.com"
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
client.configureOfflinePublishQueueing(-1)
client.configureDrainingFrequency(2)
client.configureConnectDisconnectTimeout(10)
client.configureMQTTOperationTimeout(5)

# Connect to AWS IoT Core
print("Connecting to AWS IoT Core...")
client.connect()
print("Connected!")

# Initialize I2C and ADS1115 (Analog-to-Digital Converter)
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
GAIN = 1  # Gain setting for ADC

# Publish sensor data to AWS IoT
# Publish sensor data to AWS IoT
try:
    # Calibration values
    AIR_VALUE = 28000    # Value when sensor is in air (dry)
    WATER_VALUE = 13000  # Value when sensor is in water (wet)
    
    while True:
        # Read analog value from ADS1115
        chan = AnalogIn(ads, ADS.P0)  # Read from channel 0
        raw_value = chan.value
        voltage = chan.voltage
        
        # Calculate inverted moisture percentage (higher = more moisture)
        moisture_percentage = 100 - ((raw_value - WATER_VALUE) * 100 / (AIR_VALUE - WATER_VALUE))
        moisture_percentage = max(0, min(100, moisture_percentage))  # Constrain to 0-100%
        
        # Determine soil moisture status
        if raw_value >= 25000:
            moisture_status = "Dry"
        elif raw_value >= 15000:
            moisture_status = "Moist"
        else:
            moisture_status = "Wet"
        
        # Format timestamp as HH:MM
        timestamp = time.strftime("%H:%M")
        
        # Create JSON payload
        payload = json.dumps({
            "sensor_id": sensor_id,
            "moisture_value": raw_value,
            "voltage": round(voltage, 3),
            "moisture_percentage": round(moisture_percentage, 2),
            "moisture_status": moisture_status,
            "timestamp": timestamp
        })
        
        print(f"Publishing to AWS IoT: {payload}")
        client.publish(topic, payload, 1)
        time.sleep(3)  # Send data every 3 seconds

except KeyboardInterrupt:
    print("Interrupted, cleaning up...")
    client.disconnect()
    print("Disconnected from AWS IoT Core.")