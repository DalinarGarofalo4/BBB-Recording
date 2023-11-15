FROM python:3.10-alpine
WORKDIR /app
COPY requirements.txt /app
RUN apk add --no-cache ffmpeg
RUN pip3 install -r requirements.txt
COPY . /app
RUN python JWT_generator.py
CMD ["uvicorn", "bbb-player:app", "--host","0.0.0.0","--port","8000"]

