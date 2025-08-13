#!/bin/bash


TARGET_FOLDER=$1
DOWNLOAD_URL=$2
DOWNLOADED_FILE="$TARGET_FOLDER/download.tar.gz"

# Check if the folder exists
if [ -d "$TARGET_FOLDER" ] && [ "$(ls -A $TARGET_FOLDER)" ]; then
  echo "Folder '$TARGET_FOLDER' exists and is not empty. No action needed."
else
  echo "Folder '$TARGET_FOLDER' is empty or does not exist. Proceeding with download and extraction."

  # Create the folder if it doesn't exist
  if [ ! -d "$TARGET_FOLDER" ]; then
    echo "Creating folder '$TARGET_FOLDER'..."
    mkdir -p "$TARGET_FOLDER"
  fi

  # Download the file
  echo "Downloading file from $DOWNLOAD_URL..."
  wget -O "$DOWNLOADED_FILE" "$DOWNLOAD_URL"

  # Extract the downloaded file into the folder
  echo "Extracting file into '$TARGET_FOLDER'..."
  unzip -o "$DOWNLOADED_FILE" -d "$TARGET_FOLDER"

  # Remove the downloaded file
  echo "Removing the downloaded file..."
  rm "$DOWNLOADED_FILE"

  echo "Download and extraction complete."
fi