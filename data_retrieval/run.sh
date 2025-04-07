#!/bin/bash

downloadDataFolder $MODEL_DIR $MODEL_URL
downloadDataFolder $NEWS_DATA_DIR $NEWS_DATA_URL
downloadDataFolder $FACEPAGER_DIR $FACEPAGER_URL
python retrieveModel.py