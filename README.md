# yt-dlp Android APK

YouTube 및 기타 사이트에서 동영상을 다운로드하는 안드로이드 앱입니다.

## GitHub Actions로 APK 빌드

1. 이 저장소를 GitHub에 푸시
2. Actions 탭에서 "Build Android APK" 워크플로우 실행
3. 완료 후 Artifacts에서 APK 다운로드

## 수동 빌드

```bash
pip install buildozer cython
buildozer android debug
```

## 기능

- URL로 비디오 정보 조회
- 비디오/오디오(MP3) 다운로드
- 품질 선택 (360p ~ 1080p)
- 실시간 진행률 표시
- 다운로드 파일 관리

## 지원 사이트

YouTube, TikTok, Twitter/X, Instagram, Facebook 등 1000+ 사이트
