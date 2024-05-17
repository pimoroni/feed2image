import requests
import datetime
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import Roboto
import qrcode
import math
import json
import sys

DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 448
FOOTER_MARGIN = 10
OUTPUT_DIR = "build"
TEXT_BOX_PADDING = 5
INCLUDE_TEXT = False


font = ImageFont.truetype(Roboto, 18)
width = DEFAULT_WIDTH
height = DEFAULT_HEIGHT


def text_in_rect(canvas, text, font, color, bg_color, rect, align='left', valign='top', line_spacing=1.1):
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

    # Given a rectangle, reflow and scale text to fit, centred
    while font.size > 0:
        line_height = int(font.size * line_spacing)
        max_lines = math.floor(height / line_height)
        lines = []

        # Determine if text can fit at current scale.
        words = text.split(" ")

        while len(lines) < max_lines and len(words) > 0:
            line = []

            while len(words) > 0 and font.getbbox(" ".join(line + [words[0]]))[2] <= width:
                line.append(words.pop(0))

            lines.append(" ".join(line))

        if len(lines) <= max_lines and len(words) == 0:
            # Solution is found, render the text.
            if valign == 'top':
                y = int(rect[1])
            else:
                y = int(rect[1] + (height / 2) - (len(lines) * line_height / 2) - (line_height - font.size) / 2)

            bounds = [rect[2], y, rect[0], y + len(lines) * line_height]

            for line in lines:
                tx, ty, tw, th = font.getbbox(line)
                line_width = tw
                if align == 'center':
                    x = int(rect[0] + (width / 2) - (line_width / 2))
                else:
                    x = rect[0]
                bounds[0] = min(bounds[0], x)
                bounds[2] = max(bounds[2], x + line_width)

                canvas.rectangle((
                    x + tx - TEXT_BOX_PADDING,
                    y + ty - TEXT_BOX_PADDING,
                    x + tx + tw + TEXT_BOX_PADDING,
                    y + ty + th + TEXT_BOX_PADDING
                ), fill=bg_color)
                canvas.text((x, y), line, color, font=font)
                y += line_height

            return tuple(bounds)

        font = ImageFont.truetype(font.path, font.size - 1)


# Read "WIDTHxHEIGHT" from args and set target dimensions
no_idx = 1
if "x" in sys.argv[1]:
    width, height = [int(d) for d in sys.argv[1].split("x")]
    no_idx += 1 # Assume next arg is the APOD date


try:
    apod_date = sys.argv[no_idx]
    suffix = apod_date

except (IndexError, ValueError):
    apod_date = str(datetime.datetime.now().date())
    suffix = "daily"

apod_url = f"https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&thumbs=true&date={apod_date}"
print(f"Fetching: {apod_url}")
response = requests.get(apod_url)

try:
    metadata = response.json()

except json.decoder.JSONDecodeError:
    print(f"JSON Decode error. Response: {response.text}")
    sys.exit(1)

print(apod_date, metadata)

if "thumbnail_url" in metadata:
    image_url = metadata.get("thumbnail_url")
    media_url = metadata.get("url")
else:
    image_url = metadata.get("url")
    media_url = metadata.get("hdurl")

print(f"Image URL: {image_url}")

response = requests.get(image_url, stream=True)

image = Image.open(response.raw)
w, h = image.size

new_w, new_h = max(width, height), max(width, height)

if w > h:
    new_w = int(w * (new_h / h))
else:
    new_h = int(h * (new_w / w))

image = image.resize((new_w, new_h))

"""
ratio = min(width / w, height / h)

if ratio < 1.0:
    w = int(w * ratio)
    h = int(h * ratio)

    image = image.resize((w, h))

o_x = int((width - w) / 2)
o_y = int((height - h) / 2)
"""

o_x = (width - new_w) // 2
o_y = (height - new_h) // 2

qr = qrcode.QRCode(
    version=1,
    box_size=2,
    border=2
)
qr.add_data(media_url)
qr.make(fit=True)
qr_image = qr.make_image(fill_color="black", back_color="white")
qr_w, qr_h = qr_image.size
qr_x = width - qr_w - FOOTER_MARGIN
qr_y = height - qr_h - FOOTER_MARGIN - 20

text_x = FOOTER_MARGIN
text_y = qr_y

output_image = Image.new("RGB", (width, height), color=(255, 255, 255))

draw = ImageDraw.Draw(output_image)

output_image.paste(image, (o_x, o_y))

if INCLUDE_TEXT:
    output_image.paste(qr_image, (qr_x, qr_y))

    text = metadata.get("title")

    text_in_rect(draw, text, font, (0, 0, 0), (255, 255, 255), (text_x, text_y, qr_x - FOOTER_MARGIN, text_y + qr_h), line_spacing=1.1)
    text_in_rect(draw, "nasa.gov", font, (0, 0, 0), (255, 255, 255), (qr_x, qr_y + qr_h, qr_x + qr_w, qr_y + qr_h + 20))

dimensions = ""
if (width, height) != (DEFAULT_WIDTH, DEFAULT_HEIGHT):
    dimensions = f"-{width}x{height}"

output_image.save(f"{OUTPUT_DIR}/nasa-apod{dimensions}-{suffix}.jpg")
