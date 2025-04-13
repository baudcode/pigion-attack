from ultralytics import YOLO
from PIL import Image


import paho.mqtt.client as mqtt
import os
import dotenv
from PIL import Image
import io
import base64
import json

dotenv.load_dotenv()

class MQTTClient:
    def __init__(self, image_topic: str, results_topic: str, model: "Model"):
        client = mqtt.Client()
        hostname, port = os.getenv("MQTT_SERVER").split(":")
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(hostname, int(port), 60)
        self.client = client
        self.image_topic = image_topic
        self.results_topic = results_topic
        self.model = model

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(self.image_topic)

    def on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        print(f"recv msg from client: {client.host}:{client.port} at {msg.timestamp} from topic {msg.topic}")
        if msg.topic == self.image_topic:
            base64_image = msg.payload.decode("utf-8")
            # Decode the base64 image
            image_bytes = base64.b64decode(base64_image.split(",")[1])
            # Convert the byte array to an image
            image = Image.open(io.BytesIO(image_bytes))

            print(f"Image of size {image.size} Received")
            score, num_birds = self.model(image)

            print("publishing result to topic: ", self.results_topic)
            self.client.publish(self.results_topic, json.dumps({
                "score": score,
                "numBirds": num_birds,
                "image": base64_image,
                "ts": msg.timestamp,
            }))


    def run(self):
        self.client.loop_forever()


class Model:

    def __init__(self):
        self.model = YOLO("yolo11n.onnx")
    def __call__(self, image: Image.Image):
        prediction = self.model.predict(image, conf=0.5)
        data = prediction[0].summary()

        boxes = list(filter(lambda x: x['name'] == 'bird', data))
        highest_score = max([x['confidence'] for x in boxes], default=0)
        num_birds = len(boxes)

        print("boxes: ", boxes, "highest_score: ", highest_score)
        return highest_score, num_birds
    
if __name__ == "__main__":
    model = Model()
    image_topic = "PigionImage"
    results_topic = "PigionResults"
    mqtt_client = MQTTClient(image_topic, results_topic, model)
    mqtt_client.run()
