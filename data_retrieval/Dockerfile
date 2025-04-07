# Use a lightweight base image
FROM python:3.10-slim

# Set environment variables
ENV TRANSFORMERS_CACHE=/cache
ENV HF_HUB_CACHE=/cache

# Install required tools
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    wget \
    tar \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir sentence-transformers torch
# Set the working directory
WORKDIR /app

# Copy the script into the container
COPY run.sh /app/run.sh
COPY retrieveBAA_model.py /app/retrieveModel.py
COPY downloadDataFolder.sh /app/downloadDataFolder
ENV PATH="/app:${PATH}"
# Make the script executable
RUN chmod +x /app/run.sh
RUN chmod +x /app/downloadDataFolder
RUN chmod +x /app/retrieveModel.py

# Set the default command to run the script
CMD ["/app/run.sh"]