from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
import threading
import os
import yt_dlp
from app_runtime import get_download_path

# Disable problematic clipboard providers on Android
if platform == 'android':
    os.environ['KIVY_CLIPBOARD'] = ''

Window.size = (360, 640)


class YtDlpApp(App):
    def build(self):
        self.title = "yt-dlp Downloader"

        # Main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        layout.add_widget(Label(
            text='yt-dlp Downloader',
            size_hint_y=None,
            height=40,
            font_size='20sp',
            bold=True,
            color=(1, 0.2, 0.2, 1)
        ))

        # URL input
        self.url_input = TextInput(
            hint_text='Enter video URL (YouTube, etc.)',
            multiline=False,
            size_hint_y=None,
            height=45,
            font_size='14sp',
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            hint_text_color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(self.url_input)

        # Download type selector
        type_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        type_layout.add_widget(Label(text='Type:', size_hint_x=0.3, font_size='14sp'))
        self.type_spinner = Spinner(
            text='Video',
            values=('Video', 'Audio'),
            size_hint_x=0.7,
            font_size='14sp',
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        type_layout.add_widget(self.type_spinner)
        layout.add_widget(type_layout)

        # Quality selector
        quality_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        quality_layout.add_widget(Label(text='Quality:', size_hint_x=0.3, font_size='14sp'))
        self.quality_spinner = Spinner(
            text='Best',
            values=('Best', '1080p', '720p', '480p', '360p'),
            size_hint_x=0.7,
            font_size='14sp',
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        quality_layout.add_widget(self.quality_spinner)
        layout.add_widget(quality_layout)

        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=5)

        self.info_btn = Button(
            text='Get Info',
            font_size='14sp',
            background_color=(0.2, 0.5, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        self.info_btn.bind(on_press=self.get_video_info)
        btn_layout.add_widget(self.info_btn)

        self.download_btn = Button(
            text='Download',
            font_size='14sp',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1),
            disabled=True
        )
        self.download_btn.bind(on_press=self.download_media)
        btn_layout.add_widget(self.download_btn)

        layout.add_widget(btn_layout)

        # Status label
        self.status_label = Label(
            text='Ready - Enter a URL',
            size_hint_y=None,
            height=30,
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        layout.add_widget(self.status_label)

        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=20
        )
        layout.add_widget(self.progress_bar)

        # Progress label
        self.progress_label = Label(
            text='',
            size_hint_y=None,
            height=20,
            font_size='10sp',
            color=(0.2, 0.8, 0.2, 1)
        )
        layout.add_widget(self.progress_label)

        # Video info display
        self.info_label = Label(
            text='',
            size_hint_y=None,
            height=120,
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1),
            halign='left',
            valign='top'
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        layout.add_widget(self.info_label)

        # File list
        file_list_label = Label(
            text='Downloaded Files:',
            size_hint_y=None,
            height=30,
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        layout.add_widget(file_list_label)

        # Scrollable file list
        scroll = ScrollView(size_hint=(1, 1))
        self.file_list_label = Label(
            text='No files yet',
            font_size='11sp',
            color=(0.7, 0.7, 0.7, 1),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        self.file_list_label.bind(texture_size=self.file_list_label.setter('size'))
        self.file_list_label.bind(width=lambda *x: self.file_list_label.setter('text_size')(self.file_list_label, (self.file_list_label.width, None)))
        scroll.add_widget(self.file_list_label)
        layout.add_widget(scroll)

        # Initialize
        self.video_info = None
        self.is_downloading = False
        self.download_path = None

        # Update file list
        Clock.schedule_once(lambda dt: self.update_file_list(), 1)

        return layout

    def get_video_info(self, instance=None):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = 'Please enter a URL'
            return

        self.status_label.text = 'Fetching info...'
        self.info_btn.disabled = True
        self.download_btn.disabled = True
        self.info_label.text = ''

        def fetch():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'no_check_certificate': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                self.video_info = info
                Clock.schedule_once(lambda dt: self.show_video_info(info))
            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error(str(e)))

        threading.Thread(target=fetch, daemon=True).start()

    def show_video_info(self, info):
        title = info.get('title', 'Unknown')
        uploader = info.get('uploader', 'Unknown')
        duration = info.get('duration', 0)

        # Format duration
        if duration:
            mins, secs = divmod(int(duration), 60)
            hrs, mins = divmod(mins, 60)
            if hrs > 0:
                duration_str = f"{hrs}:{mins:02d}:{secs:02d}"
            else:
                duration_str = f"{mins}:{secs:02d}"
        else:
            duration_str = "Unknown"

        self.info_label.text = f"Title: {title}\nChannel: {uploader}\nDuration: {duration_str}"
        self.status_label.text = 'Ready to download'
        self.info_btn.disabled = False
        self.download_btn.disabled = False

    def show_error(self, msg):
        self.status_label.text = 'Error occurred'
        self.info_label.text = f'Error: {msg[:200]}'
        self.info_btn.disabled = False
        self.download_btn.disabled = True

    def download_media(self, instance=None):
        if self.is_downloading:
            return

        url = self.url_input.text.strip()
        if not url:
            self.show_error('Please enter a URL')
            return

        self.is_downloading = True
        self.status_label.text = 'Preparing download...'
        self.download_btn.disabled = True
        self.progress_bar.value = 0
        self.progress_label.text = 'Starting...'

        def download():
            try:
                # Get download path
                self.download_path = get_download_path(platform)
                os.makedirs(self.download_path, exist_ok=True)

                # Determine format based on type and quality
                is_audio = (self.type_spinner.text == 'Audio')
                quality = self.quality_spinner.text

                if is_audio:
                    # Audio: use best audio without ffmpeg conversion
                    format_str = 'bestaudio[ext=m4a]/bestaudio'
                else:
                    # Video: select based on quality
                    if quality == 'Best':
                        format_str = 'best[ext=mp4]/best'
                    elif quality == '1080p':
                        format_str = 'best[height<=1080][ext=mp4]/best[height<=1080]'
                    elif quality == '720p':
                        format_str = 'best[height<=720][ext=mp4]/best[height<=720]'
                    elif quality == '480p':
                        format_str = 'best[height<=480][ext=mp4]/best[height<=480]'
                    elif quality == '360p':
                        format_str = 'best[height<=360][ext=mp4]/best[height<=360]'
                    else:
                        format_str = 'best[ext=mp4]/best'

                ydl_opts = {
                    'format': format_str,
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [self.progress_hook],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                Clock.schedule_once(lambda dt: self.download_complete())
            except Exception as e:
                Clock.schedule_once(lambda dt: self.download_error(str(e)))

        threading.Thread(target=download, daemon=True).start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)

            if total > 0:
                percent = (downloaded / total) * 100
                speed = d.get('speed', 0)

                def update_ui(dt):
                    self.progress_bar.value = percent
                    if speed:
                        speed_mb = speed / 1024 / 1024
                        self.progress_label.text = f'{percent:.1f}% ({speed_mb:.2f} MB/s)'
                    else:
                        self.progress_label.text = f'{percent:.1f}%'

                Clock.schedule_once(update_ui)
        elif d['status'] == 'finished':
            Clock.schedule_once(lambda dt: self.status_label.__setattr__('text', 'Processing...'))

    def download_complete(self):
        self.is_downloading = False
        self.status_label.text = 'Download complete!'
        self.progress_bar.value = 100
        self.progress_label.text = '100%'
        self.download_btn.disabled = False
        self.update_file_list()

    def download_error(self, msg):
        self.is_downloading = False
        self.status_label.text = 'Download failed'
        self.info_label.text = f'Error: {msg[:200]}'
        self.progress_bar.value = 0
        self.progress_label.text = ''
        self.download_btn.disabled = False

    def update_file_list(self):
        try:
            if not self.download_path:
                self.download_path = get_download_path(platform)

            if os.path.exists(self.download_path):
                files = os.listdir(self.download_path)
                if files:
                    file_list = '\n'.join([f'• {f}' for f in sorted(files)])
                    self.file_list_label.text = file_list
                else:
                    self.file_list_label.text = 'No files yet'
            else:
                self.file_list_label.text = 'Download folder not created yet'
        except Exception as e:
            self.file_list_label.text = f'Error reading files: {str(e)[:100]}'


if __name__ == '__main__':
    YtDlpApp().run()
