# yt-dlp Android APK

YouTube 및 1000+ 사이트에서 동영상/오디오를 다운로드하는 안드로이드 앱입니다.

## 🎯 주요 기능

### ✨ v2.0.0 업데이트
- 비디오/오디오 다운로드 타입 선택
- 품질 선택 (Best, 1080p, 720p, 480p, 360p)
- 실시간 진행률 바 및 다운로드 속도 표시
- 다운로드된 파일 목록 관리
- 향상된 비디오 정보 표시
- FFmpeg 의존성 제거로 더 안정적인 동작
- Android 13+ 완전 호환

### 기능 목록
- ✅ URL로 비디오 정보 조회
- ✅ 비디오/오디오 선택 다운로드
- ✅ 품질 선택 (360p ~ 1080p)
- ✅ 실시간 진행률 및 속도 표시
- ✅ 다운로드 파일 관리
- ✅ 1000+ 사이트 지원

## 📦 APK 다운로드

### GitHub Actions로 빌드
1. 이 저장소를 GitHub에 푸시
2. Actions 탭에서 "Build Android APK" 워크플로우 실행
3. 완료 후 Artifacts에서 APK 다운로드

또는 현재 브랜치를 푸시하면 자동으로 빌드가 시작됩니다.

## 🛠️ 수동 빌드

Buildozer는 Windows 네이티브 환경에서 직접 동작하지 않으므로 Ubuntu 또는 WSL2에서 빌드해야 합니다.

### Windows에서 로컬 빌드

1. 관리자 PowerShell에서 WSL 설치
```powershell
wsl --install -d Ubuntu
```

2. 시스템 재부팅

3. Ubuntu 셸에서 필수 패키지 설치
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
pip install buildozer cython==0.29.36
```

5. APK 빌드
```bash
buildozer android debug
```

생성된 APK는 `bin/` 폴더에 만들어집니다.

### Linux/macOS에서 빌드
```bash
# 필수 패키지 설치 (Ubuntu/Debian)
sudo apt-get update && sudo apt-get install -y \
    build-essential git libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev \
    libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev \
    openjdk-17-jdk python3-pip python3-venv

# 가상환경 생성 및 빌드
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install buildozer cython==0.29.36
buildozer android debug
```

## 📱 Android 호환성

- **최소 버전**: Android 5.0 (API 21)
- **권장 버전**: Android 13 (API 33) 이상
- **저장소**: 앱 전용 외부 저장소 사용 (Android 13+ 호환)
- **권한**: 인터넷 및 네트워크 상태만 필요

## 🎨 사용 방법

1. **URL 입력**: YouTube 또는 지원되는 사이트의 비디오 URL 입력
2. **타입 선택**: Video 또는 Audio 선택
3. **품질 선택**: 원하는 품질 선택 (Best, 1080p, 720p, 480p, 360p)
4. **Get Info**: 비디오 정보 확인
5. **Download**: 다운로드 시작
6. **파일 목록**: 하단에서 다운로드된 파일 확인

## 🌐 지원 사이트

YouTube, TikTok, Twitter/X, Instagram, Facebook, Vimeo, Dailymotion 등 1000+ 사이트

전체 목록: [yt-dlp 지원 사이트](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

## 🔧 기술 스택

- **UI Framework**: Kivy 2.3.0
- **다운로더**: yt-dlp
- **빌드 도구**: Buildozer
- **언어**: Python 3.10+

## 📝 개발 노트

### v2.0.0 주요 변경사항
- FFmpeg 의존성 완전 제거
  - Android에서 FFmpeg 바이너리 의존성 문제 해결
  - yt-dlp의 네이티브 포맷 선택 사용
- 비디오: MP4 포맷 우선 선택 (병합 불필요)
- 오디오: M4A 포맷 우선 선택 (변환 불필요)
- Android 13+ 스코프드 스토리지 완전 지원
- 불필요한 저장소 권한 제거

### 저장소 경로
- **Android**: `/storage/emulated/0/Android/data/org.ytdlp.ytdlp/files/Download/yt-dlp`
- **Desktop**: `~/Downloads/yt-dlp`

## 📄 라이선스

이 프로젝트는 개인 사용 및 학습 목적으로 제공됩니다.

- yt-dlp: [Unlicense](https://github.com/yt-dlp/yt-dlp/blob/master/LICENSE)
- Kivy: [MIT License](https://github.com/kivy/kivy/blob/master/LICENSE)

## 🤝 기여

이슈 및 PR은 언제나 환영합니다!

## ⚠️ 주의사항

- 저작권이 있는 콘텐츠를 다운로드할 때는 관련 법률을 준수하세요
- 개인적인 용도로만 사용하세요
- 네트워크 연결이 필요합니다
- 다운로드 속도는 인터넷 연결 상태에 따라 다릅니다
