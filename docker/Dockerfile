FROM nvidia/cuda:13.1.1-cudnn-devel-ubuntu24.04@sha256:ef8a68702fdc93f3acb12919cde4468b9df0aeea214c1c97bf57598dad558967
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-full \
    python3-venv \
    python3-pip \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements/base.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r base.txt
