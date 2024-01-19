FROM python:3.10-alpine
WORKDIR /app
COPY requirements.txt /app
COPY requirements-dev.txt /app
RUN apk add --no-cache ffmpeg make cmake openssl
RUN pip3 install -r requirements.txt -r requirements-dev.txt
COPY . /app
RUN python JWT_generator.py
RUN make generate-keys
CMD ["uvicorn", "main:app", "--host","0.0.0.0","--port","8000"]
