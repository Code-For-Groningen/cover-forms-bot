#!/bin/bash
set -e

cd /app

cd src/js && npm run start &

sleep 3

JS_PID=$!

cd /app/src/python && python main.py && kill $JS_PID 2>/dev/null || true