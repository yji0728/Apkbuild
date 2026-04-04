[app]
title = yt-dlp
package.name = ytdlp
package.domain = org.ytdlp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
requirements = python3,kivy,yt-dlp,ffmpeg
orientation = portrait
fullscreen = 1
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
p4a.branch = develop
p4a.bootstrap = sdl2
icon.filename = %(source.dir)s/icon.png
android.wakelock = True
android.manifest.activity.launchMode = singleTop
android.manifest.activity.screenOrientation = portrait
android.manifest.activity.configChanges = orientation|keyboardHidden|screenSize

[buildozer]
log_level = 2
warn_on_root = True
