#!/bin/bash

# Create directories if they don't exist
mkdir -p certs/frontend
mkdir -p certs/backend

# Generate Frontend Certificate
openssl req -x509 -newkey rsa:4096 -nodes -keyout certs/frontend/key.pem -out certs/frontend/cert.pem -sha256 -days 365 \
-subj "/C=US/ST=California/L=Mountain View/O=ULACM/OU=Development/CN=localhost" \
-addext "subjectAltName = DNS:localhost"

# Generate Backend Certificate
openssl req -x509 -newkey rsa:4096 -nodes -keyout certs/backend/key.pem -out certs/backend/cert.pem -sha256 -days 365 \
-subj "/C=US/ST=California/L=Mountain View/O=ULACM/OU=Development/CN=backend.localhost" \
-addext "subjectAltName = DNS:backend.localhost,DNS:localhost"
