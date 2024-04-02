#!/bin/bash

# Receiver build
echo "Building Docker image for receiver"
# Navigate into the directory
cd receiver
# Build the Docker image with the directory name as the tag
docker build -t receiver:latest .
# Navigate back to the parent directory
cd ..
echo "Finished building receiver"

# Storage Build

echo "Building Docker image for storage"
# Navigate into the directory
cd storage
# Build the Docker image with the directory name as the tag
docker build -t storage:latest .
# Navigate back to the parent directory
cd ..
echo "Finished building storage"


# Processing
echo "Building Docker image for processing"
# Navigate into the directory
cd processing
# Build the Docker image with the directory name as the tag
docker build -t processing:latest .
# Navigate back to the parent directory
cd ..
echo "Finished building processing"


# Audit_log
echo "Building Docker image for audit_log"
# Navigate into the directory
cd audit
# Build the Docker image with the directory name as the tag
docker build -t audit_log:latest .
# Navigate back to the parent directory
cd ..
echo "Finished building audit_log"

echo "All Docker images have been built."