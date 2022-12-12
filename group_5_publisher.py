
import json
import random
import paho.mqtt.client as mqtt
import time
from group_5_dataGenerator import DataGenerator
from datetime import datetime


class Publisher():

    def __init__(self, broker, port, topic) -> None:
        self.broker = broker
        self.port = port
        self.topic = topic
        self.data = {}
        self.dataGenerator = DataGenerator()
    
    def set_data_generator_parameters(self, base = 0, climb = 0, random_base = 0, random_sigma = 0, minute_sin_amplitude = 0, hour_sin_amplitude = 0):
        self.dataGenerator.base = base
        self.dataGenerator.climb = climb
        self.dataGenerator.random_base = random_base
        self.dataGenerator.random_sigma = random_sigma
        self.dataGenerator.minute_sin_amplitude = minute_sin_amplitude
        self.dataGenerator.hour_sin_amplitude = hour_sin_amplitude

    def createData(self) -> str:
        r1 = random.randint(1, 20)
        r2 = random.randint(1, 20)
        # interruption time and value set
        if r1 == r2:

            data = {
                "y-value": 0,
                "Timestamp": datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
            }
            print("interruption")

            data = json.dumps(data, default=str)

            return data
        else:
            data = {
                "y-value": self.dataGenerator.generate_value(),
                "Timestamp": datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
            }
            data = json.dumps(data, default=str)
            return data

    def publish(self):
        # Created Package
        self.client = mqtt.Client()
        self.client.connect(self.broker,self.port)
        print("Connected to MQTT Broker: " + str(self.broker))
        print("Publishing values to topic: " + self.topic)

        while True:
            package = self.createData()
            #convert package to dictionary
            packDict = json.loads(package)
            #checking if value is int 0 to simulate a loss of connection
            if packDict["y-value"] == 0:

                self.client.publish(self.topic, package)
                print(package)
                print("Lost connection")
                time.sleep(5)
            else:
                try:
                    self.client.publish(self.topic, package)
                    print("Published: " + str(package) + " to topic: " + self.topic)
                    time.sleep(1)
                except Exception as e:
                    print("Connection Failed:")
                    raise e
                    exit()

