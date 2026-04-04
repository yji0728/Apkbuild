from PIL import Image, ImageDraw

img = Image.new("RGB", (512, 512), "#2563EB")
draw = ImageDraw.Draw(img)

# Download arrow icon
draw.polygon([(256, 100), (180, 250), (220, 250), (220, 400), (292, 400), (292, 250), (332, 250)], fill="white")
draw.polygon([(156, 340), (256, 440), (356, 340)], fill="white")

img.save("/root/yt-dlp-android/icon.png")
img.resize((192, 192)).save("/root/yt-dlp-android/icon-192.png")
print("Icons created")
