FROM python:3.12-slim

WORKDIR /app
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install libsm6 libxext6 libgl1-mesa-dev -y
RUN apt-get install -y libglib2.0-dev
ADD pigion_model.py client.py
ADD yolo11n.onnx yolo11n.onnx
ADD .env .env

CMD ["python", "client.py"]
