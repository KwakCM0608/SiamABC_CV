#!/usr/bin/env bash
set -e

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

xhost +local:docker

sudo docker run --rm -it \
  --gpus all \
  --device=/dev/video0:/dev/video0 \
  -e DISPLAY="${DISPLAY}" \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v "${BASE_DIR}:/workspace/host" \
  -v "${BASE_DIR}/out:/workspace/out" \
  siamabc:wacv2025-demo
