#!/bin/bash

if [ "$#" -ne 3 ]; then
  echo "Usage: ./run_image_resizer.sh <image_directory> <aws_profile_name> <s3_directory>"
  exit 1
fi

docker build -t image-resizer .

IMAGE_DIRECTORY="$1"
AWS_PROFILE_NAME="$2"
S3_DIRECTORY="$3"

docker run -it --rm \
  -v "$IMAGE_DIRECTORY":/app/image_directory:ro \
  -v "${HOME}/.aws/credentials":/root/.aws/credentials:ro \
  image-resizer \
  python script.py /app/image_directory "$AWS_PROFILE_NAME" "$S3_DIRECTORY"
