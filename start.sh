#!/bin/sh

# Simple start script for backend
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT