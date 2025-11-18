# Use Bookworm base to avoid missing packages
FROM python:3.10-slim-bookworm

# Install essential build tools + ffmpeg
RUN apt-get update && \
    apt-get install -y \
    openjdk-17-jdk \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    gcc \
    python3-dev \
    ffmpeg \
    git \
    && apt-get clean \


# Java paths (keep if Java is needed later)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Python ENV
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

# Set working directory and copy code
WORKDIR /app
COPY . /app/

# Install Python packages
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install --upgrade torch==2.6.0 --extra-index-url https://download.pytorch.org/whl/cpu

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Default: keep container running so you can exec commands inside
CMD ["tail", "-f", "/dev/null"]