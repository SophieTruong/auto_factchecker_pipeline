# Use a lightweight base image
FROM debian:bullseye-slim

# Install required tools
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    wget \
    tar \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the script into the container
COPY run.sh /app/run.sh
COPY downloadDataFolder.sh /app/downloadDataFolder
ENV PATH="/app:${PATH}"
# Make the script executable
RUN chmod +x /app/run.sh
RUN chmod +x /app/downloadDataFolder

# Set the default command to run the script
CMD ["/app/run.sh"]