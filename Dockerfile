FROM pytorch/pytorch:1.10.0-cuda11.3-cudnn8-devel

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=1000 \
    FORCE_CUDA=1 \
    PYTHONPATH=""

SHELL ["/bin/bash", "-lc"]

# 네 로컬에서 확인한 SiamABC 커밋 해시로 바꿔 넣기
ARG SIAMABC_REPO=https://github.com/wvuvl/SiamABC.git
ARG SIAMABC_COMMIT=여기에_네_로컬에서_확인한_commit_hash

RUN find /etc/apt -type f \( -name "*.list" -o -name "*.sources" \) -print0 | \
    xargs -0 -r sed -i '/developer\.download\.nvidia\.com/ s/^/# /' || true

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1-mesa-glx \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# 여기서 공식 SiamABC를 고정 커밋으로 clone
RUN git clone ${SIAMABC_REPO} /workspace/SiamABC && \
    cd /workspace/SiamABC && \
    git checkout ${SIAMABC_COMMIT}

RUN python -m pip install --upgrade \
    pip==23.2.1 \
    setuptools==65.7.0 \
    wheel==0.38.4

RUN pip uninstall -y \
    opencv-python \
    opencv-python-headless \
    opencv-contrib-python \
    opencv-contrib-python-headless || true

RUN pip install \
    fire==0.3.1 \
    tqdm==4.66.5 \
    einops==0.6.1 \
    spikingjelly==0.0.0.0.12 \
    hydra-core==1.1.0 \
    omegaconf==2.1.2 \
    coloredlogs==15.0.1 \
    numpy==1.21.6 \
    pandas==1.3.5 \
    pytorch-toolbelt==0.4.3 \
    pytorchcv==0.0.65 \
    torchmetrics==0.3.2 \
    thop==0.0.31-2005241907 \
    imageio==2.20.0 \
    imageio-ffmpeg==0.4.7 \
    protobuf==3.20.3

RUN pip install \
    albumentations==1.0.0 \
    albumentations-experimental==0.0.1

RUN git clone https://github.com/facebookresearch/mobile-vision.git /opt/mobile-vision && \
    cd /opt/mobile-vision && \
    git checkout 51804a6873ae1029257cf652179c960cceeecc75 && \
    pip uninstall -y mobile-cv mobile_cv || true && \
    pip install iopath diskcache termcolor cloudpickle tabulate && \
    pip install --no-build-isolation -e /opt/mobile-vision

RUN pip install "git+https://github.com/KupynOrest/toolkit.git"

RUN pip uninstall -y \
    opencv-python \
    opencv-python-headless \
    opencv-contrib-python \
    opencv-contrib-python-headless || true && \
    pip install --no-cache-dir --force-reinstall \
    opencv-python-headless==4.8.0.74

WORKDIR /workspace/SiamABC
ENV PYTHONPATH=/opt/mobile-vision:/workspace/SiamABC

RUN python - <<'PY'
import torch
import torchvision
import cv2

print("torch:", torch.__version__)
print("torchvision:", torchvision.__version__)
print("cv2:", cv2.__version__)

from torchvision.models import regnet_x_8gf
from mobile_cv.model_zoo.models.fbnet_v2 import fbnet
from einops import rearrange
from core.models.SiamABC import SiamABCNet

print("SANITY OK")
PY

CMD ["/bin/bash"]
