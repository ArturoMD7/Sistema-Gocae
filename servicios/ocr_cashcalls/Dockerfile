FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalar dependencias del sistema requeridas para OpenCV y OCR
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

# Instalar fastapi y uvicorn para el microservicio, además de tus dependencias
RUN pip install --no-cache-dir fastapi uvicorn python-multipart
# Instalar los requirements originales
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
