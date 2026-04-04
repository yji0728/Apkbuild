from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import AsyncImage
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

import threading
import os
import yt_dlp

Window.size = (360, 640)

DOWNLOAD_PATH = "/storage/emulated/0/Download/yt-dlp"


class YtDlpApp(App):
    def build(self):
        Window.clearcolor = (0.06, 0.06, 0.06, 1)
        
        layout = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        
        layout.add_widget(Label(text="yt-dlp", size_hint_y=None, height=dp(40), font_size=dp(24), color=(1, 0.2, 0.2, 1)))
        
        self.url_input = TextInput(hint_text="Enter video URL", multiline=False, size_hint_y=None, height=dp(45), font_size=dp(14))
        self.url_input.bind(on_text_validate=self.get_info)
        layout.add_widget(self.url_input)
        
        self.info_btn = Button(text="Get Video Info", size_hint_y=None, height=dp(40), background_color=(0.2, 0.4, 0.8, 1), font_size=dp(14))
        self.info_btn.bind(on_press=self.get_info)
        layout.add_widget(self.info_btn)
        
        self.thumbnail = AsyncImage(size_hint_y=None, height=dp(180), allow_stretch=True)
        layout.add_widget(self.thumbnail)
        
        self.title_label = Label(text="", size_hint_y=None, height=dp(40), font_size=dp(12), color=(1, 1, 1, 1))
        layout.add_widget(self.title_label)
        
        format_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        self.video_btn = Button(text="Video", background_color=(0.3, 0.6, 1, 1), font_size=dp(14))
        self.video_btn.bind(on_press=lambda x: self.set_format("video"))
        self.audio_btn = Button(text="Audio (MP3)", background_color=(0.2, 0.2, 0.2, 1), font_size=dp(14))
        self.audio_btn.bind(on_press=lambda x: self.set_format("audio"))
        format_layout.add_widget(self.video_btn)
        format_layout.add_widget(self.audio_btn)
        layout.add_widget(format_layout)
        
        quality_layout = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(5))
        self.quality_btns = {}
        for q in ["Best", "1080p", "720p", "480p", "360p"]:
            btn = Button(text=q, size_hint_x=1, font_size=dp(11), background_color=(0.15, 0.15, 0.15, 1))
            btn.bind(on_press=lambda x, q=q: self.set_quality(q))
            quality_layout.add_widget(btn)
            self.quality_btns[q] = btn
        self.current_quality = "Best"
        self.quality_btns["Best"].background_color = (0.3, 0.6, 1, 1)
        layout.add_widget(quality_layout)
        
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=dp(25))
        layout.add_widget(self.progress_bar)
        
        self.status_label = Label(text="Ready", size_hint_y=None, height=dp(25), font_size=dp(12), color=(0.6, 0.6, 0.6, 1))
        layout.add_widget(self.status_label)
        
        self.download_btn = Button(text="DOWNLOAD", size_hint_y=None, height=dp(50), background_color=(0.2, 0.7, 0.2, 1), font_size=dp(18))
        self.download_btn.bind(on_press=self.start_download)
        layout.add_widget(self.download_btn)
        
        self.error_label = Label(text="", size_hint_y=None, height=dp(30), font_size=dp(10), color=(1, 0.3, 0.3, 1))
        layout.add_widget(self.error_label)
        
        layout.add_widget(Label(text="Downloaded Files:", size_hint_y=None, height=dp(30), font_size=dp(14), color=(0.8, 0.8, 0.8, 1)))
        
        self.files_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(2))
        self.files_layout.bind(minimum_height=self.files_layout.setter("height"))
        scroll = ScrollView(size_hint_y=None, height=dp(150))
        scroll.add_widget(self.files_layout)
        layout.add_widget(scroll)
        
        self.current_format = "video"
        self.download_thread = None
        self.video_info = None
        
        self.refresh_files()
        return layout
    
    def set_format(self, fmt):
        self.current_format = fmt
        if fmt == "video":
            self.video_btn.background_color = (0.3, 0.6, 1, 1)
            self.audio_btn.background_color = (0.2, 0.2, 0.2, 1)
        else:
            self.audio_btn.background_color = (0.3, 0.6, 1, 1)
            self.video_btn.background_color = (0.2, 0.2, 0.2, 1)
    
    def set_quality(self, q):
        self.current_quality = q
        for key, btn in self.quality_btns.items():
            btn.background_color = (0.15, 0.15, 0.15, 1)
        self.quality_btns[q].background_color = (0.3, 0.6, 1, 1)
    
    def get_info(self, *args):
        url = self.url_input.text.strip()
        if not url:
            return
        self.status_label.text = "Fetching info..."
        self.info_btn.disabled = True
        self.title_label.text = "Loading..."
        self.error_label.text = ""
        
        def _get():
            try:
                ydl_opts = {"quiet": True, "no_warnings": True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                Clock.schedule_once(lambda dt: self._on_info(info))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._on_error(str(e)))
        
        threading.Thread(target=_get, daemon=True).start()
    
    def _on_info(self, info):
        self.video_info = info
        self.title_label.text = info.get("title", "Unknown")[:50]
        if info.get("thumbnail"):
            self.thumbnail.source = info["thumbnail"]
        self.status_label.text = "Ready to download"
        self.info_btn.disabled = False
        self.info_btn.text = "Info Loaded"
    
    def _on_error(self, msg):
        self.error_label.text = msg[:100]
        self.status_label.text = "Error"
        self.info_btn.disabled = False
    
    def start_download(self, *args):
        url = self.url_input.text.strip()
        if not url:
            self.error_label.text = "Enter URL first"
            return
        if self.download_thread and self.download_thread.is_alive():
            return
        
        self.status_label.text = "Starting..."
        self.progress_bar.value = 0
        self.download_btn.disabled = True
        self.error_label.text = ""
        
        def _download():
            try:
                os.makedirs(DOWNLOAD_PATH, exist_ok=True)
                
                quality_map = {"Best": "best", "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]", "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]", "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]", "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]"}
                
                if self.current_format == "audio":
                    ydl_opts = {"format": "bestaudio/best", "outtmpl": os.path.join(DOWNLOAD_PATH, "%(title)s.%(ext)s"), "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}], "quiet": True}
                else:
                    ydl_opts = {"format": quality_map.get(self.current_quality, "best"), "outtmpl": os.path.join(DOWNLOAD_PATH, "%(title)s.%(ext)s"), "quiet": True, "merge_output_format": "mp4"}
                
                def progress(d):
                    if d["status"] == "downloading":
                        total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                        downloaded = d.get("downloaded_bytes", 0)
                        p = (downloaded / total * 100) if total else 0
                        Clock.schedule_once(lambda dt: self._update_progress(p))
                
                ydl_opts["progress_hooks"] = [progress]
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                Clock.schedule_once(lambda dt: self._on_complete())
            except Exception as e:
                Clock.schedule_once(lambda dt: self._on_error(str(e)))
        
        self.download_thread = threading.Thread(target=_download, daemon=True)
        self.download_thread.start()
    
    def _update_progress(self, p):
        self.progress_bar.value = p
        self.status_label.text = f"Downloading... {int(p)}%"
    
    def _on_complete(self):
        self.status_label.text = "Complete!"
        self.download_btn.disabled = False
        self.refresh_files()
    
    def _on_error(self, msg):
        self.error_label.text = msg[:100]
        self.status_label.text = "Error"
        self.download_btn.disabled = False
    
    def refresh_files(self):
        self.files_layout.clear_widgets()
        try:
            if os.path.exists(DOWNLOAD_PATH):
                files = sorted([f for f in os.listdir(DOWNLOAD_PATH) if f.endswith((".mp4", ".mp3", ".mkv", ".webm", ".m4a"))], key=lambda x: os.path.getmtime(os.path.join(DOWNLOAD_PATH, x)), reverse=True)
                for f in files:
                    file_layout = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(5))
                    file_layout.add_widget(Label(text=f[:30], size_hint_x=0.7, font_size=dp(10), color=(0.9, 0.9, 0.9, 1)))
                    size = os.path.getsize(os.path.join(DOWNLOAD_PATH, f))
                    file_layout.add_widget(Label(text=self._format_size(size), size_hint_x=0.3, font_size=dp(10), color=(0.6, 0.6, 0.6, 1)))
                    self.files_layout.add_widget(file_layout)
        except Exception as e:
            print(f"Refresh error: {e}")
    
    def _format_size(self, size):
        if size > 1073741824:
            return f"{size/1073741824:.1f}GB"
        elif size > 1048576:
            return f"{size/1048576:.1f}MB"
        elif size > 1024:
            return f"{size/1024:.1f}KB"
        return f"{size}B"


if __name__ == "__main__":
    YtDlpApp().run()
