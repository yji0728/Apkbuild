from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.image import AsyncImage
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.metrics import dp

import threading
import os
import json
import yt_dlp
from pathlib import Path


class DownloadItem(RecycleDataViewBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = dp(8)
        self.spacing = dp(8)

        self.name_label = Label(
            size_hint_x=0.6,
            halign="left",
            valign="middle",
            text_size=(self.width - dp(16), None),
            font_size=dp(14),
            color=(1, 1, 1, 1),
        )
        self.size_label = Label(
            size_hint_x=0.2,
            halign="center",
            valign="middle",
            font_size=dp(12),
            color=(0.6, 0.6, 0.6, 1),
        )
        self.delete_btn = Button(
            text="삭제",
            size_hint_x=0.2,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=dp(14),
        )
        self.delete_btn.bind(on_press=self.on_delete)

        self.add_widget(self.name_label)
        self.add_widget(self.size_label)
        self.add_widget(self.delete_btn)

    def on_delete(self, instance):
        if hasattr(self, "owner"):
            self.owner.delete_file(self.name_label.text)

    def refresh_view_attrs(self, rv, index, data):
        self.name_label.text = data.get("name", "")
        self.size_label.text = data.get("size", "")
        self.owner = rv
        return super().refresh_view_attrs(rv, index, data)


class DownloadPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(10)
        self.spacing = dp(10)
        self.download_thread = None
        self.download_id = None

        # URL 입력
        url_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5),
        )
        self.url_input = TextInput(
            hint_text="URL 입력 (YouTube, TikTok, ...)",
            multiline=False,
            font_size=dp(14),
            size_hint_x=0.75,
        )
        self.url_input.bind(on_text_validate=lambda x: self.get_info())
        self.info_btn = Button(
            text="조회",
            size_hint_x=0.25,
            background_color=(0.2, 0.5, 1, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16),
        )
        self.info_btn.bind(on_press=lambda x: self.get_info())
        url_layout.add_widget(self.url_input)
        url_layout.add_widget(self.info_btn)
        self.add_widget(url_layout)

        # 비디오 정보 영역
        self.info_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=0,
            spacing=dp(5),
        )
        self.info_layout.bind(minimum_height=self.info_layout.setter("height"))

        self.thumbnail = AsyncImage(
            size_hint_y=None,
            height=dp(180),
            allow_stretch=True,
        )
        self.title_label = Label(
            size_hint_y=None,
            height=dp(40),
            text_size=(self.width - dp(20), None),
            halign="left",
            valign="middle",
            font_size=dp(14),
            color=(1, 1, 1, 1),
        )
        self.uploader_label = Label(
            size_hint_y=None,
            height=dp(25),
            halign="left",
            font_size=dp(12),
            color=(0.7, 0.7, 0.7, 1),
        )
        self.info_layout.add_widget(self.thumbnail)
        self.info_layout.add_widget(self.title_label)
        self.info_layout.add_widget(self.uploader_label)
        self.add_widget(self.info_layout)

        # 포맷 선택
        format_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5),
        )
        self.audio_only = False
        self.video_btn = Button(
            text="비디오",
            size_hint_x=0.5,
            background_color=(0.2, 0.5, 1, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16),
        )
        self.audio_btn = Button(
            text="오디오 (MP3)",
            size_hint_x=0.5,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16),
        )
        self.video_btn.bind(on_press=lambda x: self.set_format(False))
        self.audio_btn.bind(on_press=lambda x: self.set_format(True))
        format_layout.add_widget(self.video_btn)
        format_layout.add_widget(self.audio_btn)
        self.add_widget(format_layout)

        # 품질 선택
        self.quality_spinner = Spinner(
            text="최고 화질",
            values=["최고 화질", "1080p", "720p", "480p", "360p"],
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
        )
        self.add_widget(self.quality_spinner)

        # 진행률
        progress_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            spacing=dp(5),
        )
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=dp(20))
        self.progress_label = Label(
            text="대기 중",
            size_hint_y=None,
            height=dp(25),
            font_size=dp(12),
            color=(0.7, 0.7, 0.7, 1),
        )
        self.speed_label = Label(
            text="",
            size_hint_y=None,
            height=dp(25),
            font_size=dp(12),
            color=(0.5, 0.5, 0.5, 1),
        )
        progress_layout.add_widget(self.progress_bar)
        progress_layout.add_widget(self.progress_label)
        progress_layout.add_widget(self.speed_label)
        self.add_widget(progress_layout)

        # 다운로드 버튼
        self.download_btn = Button(
            text="다운로드 시작",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=dp(18),
        )
        self.download_btn.bind(on_press=lambda x: self.start_download())
        self.add_widget(self.download_btn)

        # 에러 메시지
        self.error_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(12),
            color=(1, 0.3, 0.3, 1),
        )
        self.add_widget(self.error_label)

    def set_format(self, audio):
        self.audio_only = audio
        if audio:
            self.audio_btn.background_color = (0.2, 0.5, 1, 1)
            self.video_btn.background_color = (0.3, 0.3, 0.3, 1)
        else:
            self.video_btn.background_color = (0.2, 0.5, 1, 1)
            self.audio_btn.background_color = (0.3, 0.3, 0.3, 1)

    def get_info(self):
        url = self.url_input.text.strip()
        if not url:
            return

        self.error_label.text = ""
        self.info_btn.text = "..."
        self.info_btn.disabled = True

        def _get_info():
            try:
                ydl_opts = {"quiet": True, "no_warnings": True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                Clock.schedule_once(
                    lambda dt: self._show_info(
                        {
                            "title": info.get("title", ""),
                            "uploader": info.get("uploader", ""),
                            "thumbnail": info.get("thumbnail", ""),
                        }
                    )
                )
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_error(str(e)))
            finally:
                Clock.schedule_once(lambda dt: self._reset_info_btn())

        threading.Thread(target=_get_info, daemon=True).start()

    def _show_info(self, info):
        self.title_label.text = info["title"]
        self.uploader_label.text = info["uploader"]
        self.thumbnail.source = info["thumbnail"]
        self.info_layout.height = dp(250)

    def _show_error(self, msg):
        self.error_label.text = msg

    def _reset_info_btn(self):
        self.info_btn.text = "조회"
        self.info_btn.disabled = False

    def start_download(self):
        url = self.url_input.text.strip()
        if not url or self.download_thread and self.download_thread.is_alive():
            return

        self.error_label.text = ""
        self.progress_bar.value = 0
        self.progress_label.text = "다운로드 중..."
        self.speed_label.text = ""
        self.download_btn.disabled = True
        self.download_btn.text = "다운로드 중..."

        quality_map = {
            "최고 화질": "best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        }
        quality = quality_map.get(self.quality_spinner.text, "best")

        self.download_thread = threading.Thread(
            target=self._download, args=(url, quality, self.audio_only), daemon=True
        )
        self.download_thread.start()

    def _download(self, url, quality, audio_only):
        download_path = self._get_download_path()

        def progress_hook(d):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                progress = (downloaded / total * 100) if total else 0
                speed = d.get("speed", 0)
                eta = d.get("eta", 0)

                speed_str = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "계산 중..."
                eta_str = f"ETA: {eta}초" if eta else ""

                Clock.schedule_once(
                    lambda dt: self._update_progress(progress, speed_str, eta_str)
                )
            elif d["status"] == "finished":
                Clock.schedule_once(lambda dt: self._update_progress(100, "변환 중...", ""))

        if audio_only:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "progress_hooks": [progress_hook],
                "quiet": True,
                "no_warnings": True,
            }
        else:
            ydl_opts = {
                "format": quality,
                "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
                "progress_hooks": [progress_hook],
                "quiet": True,
                "no_warnings": True,
                "merge_output_format": "mp4",
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            Clock.schedule_once(lambda dt: self._download_complete())
        except Exception as e:
            Clock.schedule_once(lambda dt: self._download_error(str(e)))

    def _get_download_path(self):
        if platform == "android":
            from android.storage import primary_external_storage_path
            from android.permissions import Permission, request_permissions

            storage = primary_external_storage_path()
            download_path = os.path.join(storage, "Download", "yt-dlp")
        else:
            download_path = os.path.join(os.path.expanduser("~"), "yt-dlp-downloads")

        os.makedirs(download_path, exist_ok=True)
        return download_path

    def _update_progress(self, progress, speed, eta):
        self.progress_bar.value = progress
        self.speed_label.text = f"{speed} {eta}"

    def _download_complete(self):
        self.progress_label.text = "완료!"
        self.speed_label.text = ""
        self.download_btn.disabled = False
        self.download_btn.text = "다운로드 시작"

        # Refresh library
        app = App.get_running_app()
        if hasattr(app, "library_panel"):
            app.library_panel.refresh()

    def _download_error(self, msg):
        self.progress_label.text = "오류"
        self.error_label.text = msg
        self.download_btn.disabled = False
        self.download_btn.text = "다운로드 시작"


class LibraryPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        self.rv = RecycleView()
        self.rv.data = []
        self.rv.viewclass = DownloadItem
        self.rv.add_widget(
            RecycleBoxLayout(
                default_size=(None, dp(60)),
                default_size_hint=(1, None),
                size_hint_y=None,
                orientation="vertical",
            )
        )
        self.rv.bind(minimum_height=self.rv.children[0].setter("height"))

        self.empty_label = Label(
            text="다운로드한 파일이 없습니다",
            color=(0.5, 0.5, 0.5, 1),
            font_size=dp(16),
        )

        self.add_widget(self.rv)
        self.add_widget(self.empty_label)

        self.refresh()

    def on_enter(self):
        self.refresh()

    def refresh(self):
        download_path = self._get_download_path()
        files = []

        if os.path.exists(download_path):
            for f in os.listdir(download_path):
                if f.endswith((".mp4", ".mp3", ".mkv", ".webm", ".m4a")):
                    filepath = os.path.join(download_path, f)
                    size = os.path.getsize(filepath)
                    files.append({"name": f, "size": self._format_size(size)})

        self.rv.data = files
        self.empty_label.visible = len(files) == 0
        self.rv.visible = len(files) > 0

    def _get_download_path(self):
        if platform == "android":
            from android.storage import primary_external_storage_path
            storage = primary_external_storage_path()
            return os.path.join(storage, "Download", "yt-dlp")
        else:
            return os.path.join(os.path.expanduser("~"), "yt-dlp-downloads")

    def _format_size(self, size):
        if size > 1073741824:
            return f"{size / 1073741824:.1f} GB"
        elif size > 1048576:
            return f"{size / 1048576:.1f} MB"
        elif size > 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size} B"

    def delete_file(self, filename):
        download_path = self._get_download_path()
        filepath = os.path.join(download_path, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        self.refresh()


class YtDlpApp(App):
    def build(self):
        Window.clearcolor = (0.04, 0.04, 0.04, 1)

        self.panel = TabbedPanel(do_default_tab=False)

        # 다운로드 탭
        download_tab = TabbedPanelHeader(text="다운로드")
        self.download_panel = DownloadPanel()
        download_tab.add_widget(self.download_panel)

        # 라이브러리 탭
        library_tab = TabbedPanelHeader(text="라이브러리")
        self.library_panel = LibraryPanel()
        library_tab.add_widget(self.library_panel)

        self.panel.add_widget(download_tab)
        self.panel.add_widget(library_tab)

        self.panel.bind(current_tab=self.on_tab_change)

        return self.panel

    def on_tab_change(self, instance, value):
        if value.text == "라이브러리":
            self.library_panel.refresh()


if __name__ == "__main__":
    YtDlpApp().run()
