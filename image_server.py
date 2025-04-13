import paho.mqtt.publish as publish
import os
import dotenv
import base64
from PIL import Image
import io
from datetime import datetime
from picamera2 import Picamera2
import time

picam2 = Picamera2()
conf = picam2.create_still_configuration(main={'size': (1920, 1080), 'format':'RGB888'})
picam2.configure(conf)
picam2.start()

def take_image():
    array = picam2.capture_array('main')
    array = array[:, :, ::-1]
    return Image.fromarray(array)

def img2b64(image: Image.Image) -> str:
    stream = io.BytesIO()
    image.save(stream, "JPEG", quality=80)
    stream.seek(0)
    data = stream.read()
    image = base64.b64encode(data).decode("utf-8")
    image = f"data:image/jpeg;base64,{image}"
    return image

dotenv.load_dotenv()

hostname, port = os.getenv("MQTT_SERVER").split(":")  #Write Server IP Address
MQTT_PATH = "PigionImage"

while True:
    # image to base64 data html
    image = take_image()
    data = img2b64(image)
    
    print(f"publish image {datetime.utcnow()}")
    publish.single(MQTT_PATH, data, hostname=hostname, port=int(port))
    time.sleep(2)