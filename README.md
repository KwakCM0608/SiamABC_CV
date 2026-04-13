# SiamABC Webcam Face Tracking (Docker)

SiamABC (WACV 2025) 기반 **웹캠 실시간 트래킹**

---

## Requirements

### 1. OS

* Ubuntu 20.04 / 22.04

### 2. 필수 설치

* Docker
* NVIDIA GPU + Driver
* NVIDIA Container Toolkit

### 3. GPU 확인

```bash
nvidia-smi
```

---

## Quick Start

### 1. Clone

```bash
git clone git@github.com:KwakCM0608/SiamABC_CV.git
cd SiamABC_CV
```

---

### 2. Docker Build

```bash
docker build -t siamabc:wacv2025-demo .
```

---

### 3. X11 권한

```bash
xhost +local:docker
```

---

### 4. Docker 실행

```bash
docker run --rm -it \
  --gpus all \
  --device=/dev/video0:/dev/video0 \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd):/workspace/host \
  -v $(pwd)/out:/workspace/out \
  siamabc:wacv2025-demo
```

---

### 5. 컨테이너 내부에서 실행

```bash
python /workspace/host/webcam_siamabc_track.py
```

---

## 사용 방법

1. 실행하면 웹캠 화면이 뜸
2. **Tracking할 대상을 마우스로 드래그해서 선택**
3. ENTER 또는 SPACE로 확정
4. Tracking

---

## 키 조작

* `q` : 종료
* `r` : Tracking 대상 다시 선택 (재초기화)

---

## 디렉토리 구조

```bash
SiamABC_CV/
├── Dockerfile
├── webcam_roi_test.py
├── webcam_siamabc_track.py
├── siamabc_src/              # SiamABC 공식 코드 포함
│   ├── assets/
│   ├── core/
│   ├── realtime_test.py
│   └── ...
├── out/                      # 결과 저장 (자동 생성)
└── README.md
```

---

## Tips

* S_Tiny 모델 사용
* 대상이 크게 가려지면 드리프트 발생 → `r`로 재선택

---

## 구조 설명

Pipeline:

```
Webcam → ROI 선택 → SiamABC initialize → frame별 update → bbox 출력
```

---

## License

SiamABC 원본 저장소를 기반으로 구성됨
