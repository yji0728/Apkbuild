from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window
import threading
import os
import yt_dlp

# Disable problematic clipboard providers on Android
if platform == 'android':
    import os
    os.environ['KIVY_CLIPBOARD'] = ''

Window.size = (360, 640)

class SimpleYtDlpApp(App):
    def build(self):
        self.title = "Simple yt-dlp Downloader"
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        layout.add_widget(Label(
            text='Simple yt-dlp',
            size_hint_y=None,
            height=40,
            font_size='20sp',
            bold=True,
            color=(1, 0.2, 0.2, 1)  # Red like yt-dlp logo
        ))
        
        # URL input
        self.url_input = TextInput(
            hint_text='Enter YouTube or video URL',
            multiline=False,
            size_hint_y=None,
            height=45,
            font_size='14sp',
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1),
            hint_text_color=(0.7, 0.7, 0.7, 1)
        )
        self.url_input.bind(on_text_validate=self.on_enter)
        layout.add_widget(self.url_input)
        
        # Buttons layout
        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=5)
        
        # Get info button
        self.info_btn = Button(
            text='Get Info',
            font_size='14sp',
            background_color=(0.2, 0.5, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        self.info_btn.bind(on_press=self.get_video_info)
        btn_layout.add_widget(self.info_btn)
        
        # Download button
        self.download_btn = Button(
            text='Download MP3',
            font_size='14sp',
            background_color=(0.2, 0.8, 0.2, 1),
            color=(1, 1, 1, 1),
            disabled=True
        )
        self.download_btn.bind(on_press=self.download_audio)
        btn_layout.add_widget(self.download_btn)
        
        layout.add_widget(btn_layout)
        
        # Status label
        self.status_label = Label(
            text='Ready - Enter a URL and click Get Info',
            size_hint_y=None,
            height=30,
            font_size='12sp',
            color=(0.8, 0.8, 0.8, 1),
            halign='left'
        )
        layout.add_widget(self.status_label)
        
        # Result/info display
        self.result_label = Label(
            text='',
            size_hint_y=None,
            height=100,
            font_size='12sp',
            color=(0.9, 0.9, 0.9, 1),
            halign='left',
            valign='top'
        )
        layout.add_widget(self.result_label)
        
        # Progress bar (hidden by default)
        self.progress_bar = Label(
            text='',
            size_hint_y=None,
            height=20,
            font_size='10sp',
            color=(0.2, 0.8, 0.2, 1),
            halign='left'
        )
        layout.add_widget(self.progress_bar)
        
        # Initialize
        self.video_info = None
        self.is_downloading = False
        
        return layout
    
    def on_enter(self, instance):
        self.get_video_info()
    
    def get_video_info(self):
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = 'Please enter a URL'
            return
            
        # Reset UI
        self.status_label.text = 'Fetching video info...'
        self.info_btn.disabled = True
        self.download_btn.disabled = True
        self.result_label.text = ''
        self.progress_bar.text = ''
        
        def fetch_info():
            try:
                # Configure yt-dlp options
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'no_check_certificate': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                
                # Store info for download
                self.video_info = info
                
                # Update UI on main thread
                Clock.schedule_once(lambda dt: self.update_info_display(info))
            except Exception as e:
                error_msg = str(e)
                if 'Unsupported URL' in error_msg:
                    error_msg = 'Unsupported URL. Please check the link.'
                elif 'HTTP Error 404' in error_msg:
                    error_msg = 'Video not found or unavailable.'
                elif 'Video unavailable' in error_msg:
                    error_msg = 'Video is unavailable or private.'
                Clock.schedule_once(lambda dt: self.show_error(error_msg))
        
        # Run in background thread
        threading.Thread(target=fetch_info, daemon=True).start()
    
    def update_info_display(self, info):
        title = info.get('title', 'Unknown Title')
        uploader = info.get('uploader', 'Unknown')
        duration = info.get('duration', 0)
        view_count = info.get('view_count', 0)
        
        # Format duration
        if duration and isinstance(duration, (int, float)) and duration > 0:
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            if hours > 0:
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes:02d}:{seconds:02d}"
        else:
            duration_str = "Unknown"
        
        # Format view count
        if view_count:
            if view_count >= 1000000:
                views_str = f"{view_count/1000000:.1f}M"
            elif view_count >= 1000:
                views_str = f"{view_count/1000:.1f}K"
            else:
                views_str = str(view_count)
        else:
            views_str = "Unknown"
        
        # Update display
        self.result_label.text = f"Title: {title}\nChannel: {uploader}\nDuration: {duration_str}\nViews: {views_str}"
        self.status_label.text = 'Info loaded! Ready to download MP3'
        self.info_btn.disabled = False
        self.download_btn.disabled = False
        self.progress_bar.text = ''
    
    def show_error(self, msg):
        self.status_label.text = 'Error occurred'
        self.result_label.text = f'Error: {msg[:150]}...' if len(msg) > 150 else f'Error: {msg}'
        self.info_btn.disabled = False
        self.download_btn.disabled = True
        self.progress_bar.text = ''
    
    def download_audio(self):
        if self.is_downloading:
            return
            
        if not self.video_info:
            self.show_error('No video information available. Please get info first.')
            return
            
        url = self.url_input.text.strip()
        if not url:
            self.show_error('Please enter a URL')
            return
            
        # Set downloading state
        self.is_downloading = True
        self.status_label.text = 'Preparing download...'
        self.download_btn.disabled = True
        self.progress_bar.text = 'Starting...'
        self.result_label.text = ''
        
        def download_audio():
            try:
                # Create download directory
                download_path = "/storage/emulated/0/Download/yt-dlp"
                os.makedirs(download_path, exist_ok=True)
                
                # Configure yt-dlp for audio download
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                    'no_warnings': True,
                }
                
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                        downloaded = d.get('downloaded_bytes', 0)
                        
                        if total > 0:
                            percent = (downloaded / total) * 100
                            speed = d.get('speed', 0)
                            if speed:
                                speed_mb = speed / 1024 / 1024
                                Clock.schedule_once(
                                    lambda dt: self.update_progress(percent, speed_mb)
                                )
                            else:
                                Clock.schedule_once(
                                    lambda dt: self.update_progress(percent, None)
                                )
                        else:
                            # Show downloaded size if total unknown
                            mb = downloaded / 1024 / 1024
                            Clock.schedule_once(
                                lambda dt: self.update_progress(None, mb)
                            )
                    elif d['status'] == 'finished':
                        Clock.schedule_once(lambda dt: self.download_complete())
                    elif d['status'] == 'error':
                        Clock.schedule_once(lambda dt: self.show_error('Download failed'))
                
                ydl_opts['progress_hooks'] = [progress_hook]
                
                # Perform download
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
            except Exception as e:
                error_msg = str(e)
                if 'Unsupported URL' in error_msg:
                    error_msg = 'Unsupported URL'
                elif 'HTTP Error 404' in error_msg:
                    error_msg = 'Video not found'
                elif 'Video unavailable' in error_msg:
                    error_msg = 'Video unavailable'
                elif 'ffmpeg' in error_msg.lower():
                    error_msg = 'FFmpeg not found'
                Clock.schedule_once(lambda dt: self.show_error(error_msg))
            finally:
                # Reset downloading state
                self.is_downloading = False
        
        # Run download in background thread
        threading.Thread(target=download_audio, daemon=True).start()
    
    def update_progress(self, percent, speed_mb=None):
        if percent is not None:
            if speed_mb is not None:
                self.progress_bar.text = f'{percent:.1f}% ({speed_mb:.1f} MB/s)'
            else:
                self.progress_bar.text = f'{percent:.1f}%'
        elif speed_mb is not None:
            self.progress_bar.text = f'{speed_mb:.1f} MB downloaded'
        else:
            self.progress_bar.text = 'Processing...'
    
    def download_complete(self):
        self.is_downloading = False
        self.status_label.text = 'Download complete!'
        self.progress_bar.text = ''
        self.result_label.text = 'Audio saved to:\n/storage/emulated/0/Download/yt-dlp\n\nEnter another URL to download more.'
        self.download_btn.disabled = False
        self.download_btn.text = 'Download Another'

if __name__ == '__main__':
    SimpleYtDlpApp().run()