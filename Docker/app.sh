#!/bin/sh

celery -A tasks purge -f
celery -A tasks worker --loglevel=INFO --concurrency=4 &

# Wait for 5 seconds
sleep 5

# Run the main Python application
python main.py
