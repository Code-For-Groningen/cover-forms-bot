#!/bin/bash

cd js && npm run start &

# Wait a bit for the process to start
sleep 2

# Export the PID as an environment variable
export WAPP_PID=$!
export COVER_EMAIL="EMAIL-HERE"
export COVER_PASSWORD="PASSWORD-HERE"

cd python && python main.py

kill $WAPP_PID 2>/dev/null