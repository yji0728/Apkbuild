import os
import posixpath


def get_download_path(platform_name, android_external_dir=None):
    if platform_name == "android":
        base_dir = android_external_dir or _resolve_android_external_dir()
        if base_dir:
            normalized_base_dir = base_dir.replace("\\", "/").rstrip("/")
            return posixpath.join(normalized_base_dir, "yt-dlp")

    return os.path.join(os.path.expanduser("~"), "Downloads", "yt-dlp")


def build_download_options(download_path, audio_only, progress_hook=None):
    output_template = os.path.join(download_path, "%(title)s.%(ext)s")
    if "/" in download_path:
        output_template = f"{download_path}/%(title)s.%(ext)s"

    options = {
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True,
    }

    if progress_hook is not None:
        options["progress_hooks"] = [progress_hook]

    if audio_only:
        options["format"] = "bestaudio[ext=m4a]/bestaudio[acodec!=none]/bestaudio/best"
    else:
        options["format"] = (
            "best[ext=mp4][acodec!=none][vcodec!=none]/"
            "best[acodec!=none][vcodec!=none]/best"
        )

    return options


def _resolve_android_external_dir():
    try:
        from jnius import autoclass

        Environment = autoclass("android.os.Environment")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")

        activity = PythonActivity.mActivity
        external_dir = activity.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)
        if external_dir is not None:
            return external_dir.getAbsolutePath()
    except Exception as exc:
        print(f"Android storage path error: {exc}")

    return None