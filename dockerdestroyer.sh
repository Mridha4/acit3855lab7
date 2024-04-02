#!/bin/bash

# Receiver build
echo "Killing Docker image for receiver"
# Navigate into the directory
cd receiver
# Remove the Docker image with the directory name as the tag
docker image rm -f receiver:latest
# Navigate back to the parent directory
cd ..
echo "Finished removing receiver image"

# Storage Build

echo "Killing Docker image for storage"
# Navigate into the directory
cd storage
# Build the Docker image with the directory name as the tag
docker image rm -f storage:latest
# Navigate back to the parent directory
cd ..
echo "Finished killing storage"


# Processing
echo "Killing Docker image for processing"
# Navigate into the directory
cd processing
# Build the Docker image with the directory name as the tag
docker image rm -f processing:latest
# Navigate back to the parent directory
cd ..
echo "Finished killing processing"


# Audit_log
echo "Killing Docker image for audit_log"
# Navigate into the directory
cd audit
# Build the Docker image with the directory name as the tag
docker image rm -f audit_log:latest
# Navigate back to the parent directory
cd ..
echo "Finished killing audit_log"

echo "All Docker images have been killed."