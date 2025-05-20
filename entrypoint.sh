#!/bin/bash
set -e

cd /app/src/js && npm run start &
sleep 3

export WAPP_PID=$!
cd /app/src/python && python main.py && kill $WAPP_PID 2>/dev/null || true