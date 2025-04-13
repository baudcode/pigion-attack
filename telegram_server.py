import requests
from PIL import Image
import io
from fastapi import FastAPI
from pydantic import BaseModel
import base64
from typing import Optional
import dotenv
import os

dotenv.load_dotenv()

DEFAULT_CHAT_ID = os.getenv("CHAT_ID")
bot_token = os.getenv("TELEGRAM_TOKEN")

def send_message(message: str, chat_id: int = DEFAULT_CHAT_ID):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': message
    }

    response = requests.post(url, data=payload)
    assert response.status_code == 200, f"Error: {response.status_code}"
    data = response.json()
    assert data['ok'], f"Error: {data['description']}"
    print("Message sent successfully!")
    return data

def send_image(image: Image.Image, chat_id: int = DEFAULT_CHAT_ID):

    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    stream = io.BytesIO()
    data = image.save(stream, format='JPEG')
    stream.seek(0)
    payload = {'chat_id': chat_id}
    files = {'photo': stream}
    response = requests.post(url, data=payload, files=files)
    assert response.status_code == 200, f"Error: {response.status_code}"
    data = response.json()
    assert data['ok'], f"Error: {data['description']}"
    print("Image sent successfully!")
    return data

class ImageData(BaseModel):
    image: str
    msg: Optional[str] = None
    chat_id: Optional[int] = None

    def decode_image(self):
        # Decode the base64 image
        image_bytes = base64.b64decode(self.image.split(",")[1])
        # Convert the byte array to an image
        return Image.open(io.BytesIO(image_bytes))

app = FastAPI()

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/telegram/message")
def send_message_endpoint(msg: str, chat_id: Optional[int] = None):
    send_message(msg, chat_id=chat_id or DEFAULT_CHAT_ID)
    return {"status": "ok"}

@app.post("/telegram/image")
def send_image_base64_endpoint(data: ImageData):
    image = data.decode_image()
    send_image(image, chat_id=data.chat_id or DEFAULT_CHAT_ID)

    if data.msg:
        send_message(data.msg)

    return {"status": "ok"}