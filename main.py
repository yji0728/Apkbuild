from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.metrics import dp

import threading
import os
import yt_dlp
from app_runtime import build_download_options, get_download_path

if platform != "android":
    Window.size = (360, 640)


class DownloadItem(RecycleDataViewBehavior, BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = dp(8)
        self.spacing = dp(8)
        self.delete_callback = None
        self.file_name = ""

        self.name_label = Label(
            size_hint_x=0.6,
            halign="left",
            valign="middle",
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
            text="Del",
            size_hint_x=0.2,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1),
            font_size=dp(12),
        )
        self.delete_btn.bind(on_press=self.on_delete)

        self.add_widget(self.name_label)
        self.add_widget(self.size_label)
        self.add_widget(self.delete_btn)

    def on_delete(self, instance):
        if self.delete_callback and self.file_name:
            self.delete_callback(self.file_name)

    def refresh_view_attrs(self, rv, index, data):
        self.name_label.text = data.get("name", "")
        self.size_label.text = data.get("size", "")
        self.delete_callback = data.get("delete_callback")
        self.file_name = data.get("name", "")
        return super().refresh_view_attrs(rv, index, data)


class DownloadPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(10)
        self.spacing = dp(10)
        self.download_thread = None
        self.audio_only = False

        # Title
        title = Label(
            text="yt-dlp Downloader",
            size_hint_y=None,
            height=dp(40),
            font_size=dp(20),
            color=(0.2, 0.6, 1, 1),
        )
        self.add_widget(title)

        url_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(45),
            spacing=dp(5),
        )
        self.url_input = TextInput(
            hint_text="YouTube URL",
            multiline=False,
            font_size=dp(14),
            size_hint_x=0.75,
        )
        self.url_input.bind(on_text_validate=lambda x: self.get_info())
        self.info_btn = Button(
            text="Info",
            size_hint_x=0.25,
            background_color=(0.2, 0.5, 1, 1),
            color=(1, 1, 1, 1),
            font_size=dp(14),
        )
        self.info_btn.bind(on_press=lambda x: self.get_info())
        url_layout.add_widget(self.url_input)
        url_layout.add_widget(self.info_btn)
        self.add_widget(url_layout)

        # Info display
        self.info_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            spacing=dp(5),
        )
        self.info_layout.bind(minimum_height=self.info_layout.setter("height"))

        self.thumbnail = AsyncImage(
            size_hint_y=None,
            height=dp(120),
            allow_stretch=True,
        )
        self.title_label = Label(
            size_hint_y=None,
            height=dp(40),
            halign="left",
            valign="middle",
            font_size=dp(12),
            color=(1, 1, 1, 1),
        )
        self.uploader_label = Label(
            size_hint_y=None,
            height=dp(20),
            halign="left",
            font_size=dp(10),
            color=(0.7, 0.7, 0.7, 1),
        )
        self.info_layout.add_widget(self.thumbnail)
        self.info_layout.add_widget(self.title_label)
        self.info_layout.add_widget(self.uploader_label)
        self.add_widget(self.info_layout)

        # Format buttons
        format_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(5),
        )
        self.video_btn = Button(
            text="Video",
            size_hint_x=0.5,
            background_color=(0.2, 0.5, 1, 1),
            color=(1, 1, 1, 1),
            font_size=dp(14),
        )
        self.audio_btn = Button(
            text="Audio",
            size_hint_x=0.5,
            background_color=(0.3, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=dp(14),
        )
        self.video_btn.bind(on_press=lambda x: self.set_format(False))
        self.audio_btn.bind(on_press=lambda x: self.set_format(True))
        format_layout.add_widget(self.video_btn)
        format_layout.add_widget(self.audio_btn)
        self.add_widget(format_layout)

        # Progress
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=dp(20))
        self.progress_label = Label(
            text="Ready",
            size_hint_y=None,
            height=dp(25),
            font_size=dp(12),
            color=(0.7, 0.7, 0.7, 1),
        )
        self.add_widget(self.progress_bar)
        self.add_widget(self.progress_label)

        # Download button
        self.download_btn = Button(
            text="Download",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16),
        )
        self.download_btn.bind(on_press=lambda x: self.start_download())
        self.add_widget(self.download_btn)

        # Error
        self.error_label = Label(
            text="",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(10),
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
        self.title_label.text = "Loading..."

        def _get_info():
            try:
                ydl_opts = {"quiet": True, "no_warnings": True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                Clock.schedule_once(
                    lambda dt: self._show_info({
                        "title": info.get("title", "Unknown"),
                        "uploader": info.get("uploader", ""),
                        "thumbnail": info.get("thumbnail", ""),
                    })
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

    def _show_error(self, msg):
        self.error_label.text = msg
        self.title_label.text = "Error"

    def _reset_info_btn(self):
        self.info_btn.text = "Info"
        self.info_btn.disabled = False

    def start_download(self):
        url = self.url_input.text.strip()
        if not url:
            return

        self.error_label.text = ""
        self.progress_bar.value = 0
        self.progress_label.text = "Starting..."
        self.download_btn.disabled = True
        self.download_btn.text = "Downloading..."

        self.download_thread = threading.Thread(
            target=self._download, args=(url, self.audio_only), daemon=True
        )
        self.download_thread.start()

    def _download(self, url, audio_only):
        download_path = get_download_path(platform)
        
        def progress_hook(d):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)
                progress = (downloaded / total * 100) if total else 0
                Clock.schedule_once(lambda dt: self._update_progress(progress))

        try:
            os.makedirs(download_path, exist_ok=True)

            ydl_opts = build_download_options(download_path, audio_only, progress_hook)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            Clock.schedule_once(lambda dt: self._download_complete())
        except Exception as e:
            Clock.schedule_once(lambda dt: self._download_error(str(e)))

    def _update_progress(self, progress):
        self.progress_bar.value = progress
        self.progress_label.text = f"Downloading... {int(progress)}%"

    def _download_complete(self):
        self.progress_label.text = "Complete!"
        self.download_btn.disabled = False
        self.download_btn.text = "Download"

        app = App.get_running_app()
        if hasattr(app, "library_panel"):
            app.library_panel.refresh()

    def _download_error(self, msg):
        self.progress_label.text = "Error"
        self.error_label.text = msg
        self.download_btn.disabled = False
        self.download_btn.text = "Download"


class LibraryPanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        self.rv = RecycleView()
        self.rv.data = []
        self.rv.viewclass = DownloadItem
        layout = RecycleBoxLayout(
            default_size=(None, dp(60)),
            default_size_hint=(1, None),
            size_hint_y=None,
            orientation="vertical",
        )
        layout.bind(minimum_height=layout.setter("height"))
        self.rv.layout_manager = layout
        self.rv.add_widget(layout)

        self.empty_label = Label(
            text="No downloads yet",
            color=(0.5, 0.5, 0.5, 1),
            font_size=dp(14),
        )

        self.add_widget(self.rv)
        self.add_widget(self.empty_label)

    def refresh(self):
        download_path = get_download_path(platform)
        files = []

        try:
            if os.path.exists(download_path):
                for f in sorted(os.listdir(download_path), key=lambda x: os.path.getmtime(os.path.join(download_path, x)), reverse=True):
                    if f.endswith((".mp4", ".mp3", ".mkv", ".webm", ".m4a")):
                        filepath = os.path.join(download_path, f)
                        size = os.path.getsize(filepath)
                        files.append({
                            "name": f,
                            "size": self._format_size(size),
                            "delete_callback": self.delete_file,
                        })
        except Exception as e:
            print(f"Refresh error: {e}")

        self.rv.data = files
        self.empty_label.opacity = 1 if len(files) == 0 else 0

    def _format_size(self, size):
        if size > 1073741824:
            return f"{size / 1073741824:.1f} GB"
        elif size > 1048576:
            return f"{size / 1048576:.1f} MB"
        elif size > 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size} B"

    def delete_file(self, filename):
        download_path = get_download_path(platform)
        filepath = os.path.join(download_path, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Delete error: {e}")
        self.refresh()


class YtDlpApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

        self.panel = TabbedPanel(do_default_tab=False)

        download_tab = TabbedPanelHeader(text="Download")
        self.download_panel = DownloadPanel()
        download_tab.add_widget(self.download_panel)

        library_tab = TabbedPanelHeader(text="Library")
        self.library_panel = LibraryPanel()
        library_tab.add_widget(self.library_panel)

        self.panel.add_widget(download_tab)
        self.panel.add_widget(library_tab)

        self.panel.bind(current_tab=self.on_tab_change)

        return self.panel

    def on_tab_change(self, instance, value):
        if value.text == "Library":
            self.library_panel.refresh()


if __name__ == "__main__":
    YtDlpApp().run()
