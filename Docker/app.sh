#!/bin/sh

celery -A tasks worker --loglevel=INFO --concurrency=4 &

python main.py
