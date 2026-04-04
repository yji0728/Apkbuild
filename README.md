# yt-dlp Android APK

YouTube 및 기타 사이트에서 동영상을 다운로드하는 안드로이드 앱입니다.

## GitHub Actions로 APK 빌드

1. 이 저장소를 GitHub에 푸시
2. Actions 탭에서 "Build Android APK" 워크플로우 실행
3. 완료 후 Artifacts에서 APK 다운로드

## 수동 빌드

Buildozer는 Windows 네이티브 환경에서 직접 동작하지 않으므로 Ubuntu 또는 WSL2에서 빌드해야 합니다.

### Windows에서 로컬 빌드

1. 관리자 PowerShell에서 `wsl --install -d Ubuntu` 실행
2. 시스템 재부팅
3. Ubuntu 셸에서 아래 패키지 설치

```bash
sudo apt-get update
sudo apt-get install -y \
	build-essential git libsdl2-dev libsdl2-image-dev \
	libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev \
	libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
	libgstreamer1.0-0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
	openjdk-17-jdk unzip zip curl wget python3-pip python3-venv
```

4. 프로젝트 폴더에서 가상환경 및 빌드 도구 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install buildozer cython
```

5. APK 빌드

```bash
buildozer android debug
```

생성된 APK는 `bin/` 폴더에 만들어집니다.

## 기능

- URL로 비디오 정보 조회
- 비디오/오디오 다운로드
- 품질 선택 (360p ~ 1080p)
- 실시간 진행률 표시
- 다운로드 파일 관리

## Android 동작 메모

- Android 13 이상에서도 동작하도록 앱 전용 외부 저장소 경로를 사용합니다.
- 비디오는 ffmpeg 병합 없이 재생 가능한 단일 파일 포맷을 우선 다운로드합니다.
- 오디오는 기기 내 ffmpeg 바이너리 의존성을 없애기 위해 원본 오디오 포맷으로 저장합니다.

## 지원 사이트

YouTube, TikTok, Twitter/X, Instagram, Facebook 등 1000+ 사이트
