FROM ubuntu:24.04

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-tk \
    python3-dev \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxft2 \
    libxcb1 \
    libx11-xcb1 \
    libxau6 \
    libxdmcp6 \
    fonts-dejavu-core \
    xvfb \
    xauth \
    x11vnc \
    x11-utils \
    fluxbox \
    novnc \
    websockify \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN /usr/bin/python3 -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

EXPOSE 6080 5900

CMD ["./start.sh"]