import requests
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import Roboto
import qrcode
import math
import sys

DEFAULT_WIDTH = 600
DEFAULT_HEIGHT = 448
FOOTER_MARGIN = 10
OUTPUT_DIR = "build"


font = ImageFont.truetype(Roboto, 18)
width = DEFAULT_WIDTH
height = DEFAULT_HEIGHT


def text_in_rect(canvas, text, font, color, rect, align='left', valign='top', line_spacing=1.1):
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

    # Given a rectangle, reflow and scale text to fit, centred
    while font.size > 0:
        space_width = font.getbbox(" ")[2]
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
                line_width = font.getbbox(line)[2]
                if align == 'center':
                    x = int(rect[0] + (width / 2) - (line_width / 2))
                else:
                    x = rect[0]
                bounds[0] = min(bounds[0], x)
                bounds[2] = max(bounds[2], x + line_width)
                canvas.text((x, y), line, color, font=font)
                y += line_height

            return tuple(bounds)

        font = ImageFont.truetype(font.path, font.size - 1)


# Read "WIDTHxHEIGHT" from args and set target dimensions
no_idx = 1
if "x" in sys.argv[1]:
    width, height = [int(d) for d in sys.argv[1].split("x")]
    no_idx += 1 # Assume next arg is the XKCD number


try:
    number = int(sys.argv[no_idx])
    metadata = requests.get(f"https://xkcd.com/{number}/info.0.json").json()
    suffix = str(number)

except (IndexError, ValueError):
    metadata = requests.get("https://xkcd.com/info.0.json").json()
    suffix = "daily"


response = requests.get(metadata.get("img"), stream=True)

image = Image.open(response.raw)
w, h = image.size
ratio = min(width / w, (height - 100) / h)

if ratio < 1.0:
    w = int(w * ratio)
    h = int(h * ratio)

    image = image.resize((w, h))

o_x = int((width - w) / 2)
o_y = int((height - 100 - h) / 2)

print(metadata)

qr = qrcode.QRCode(
    version=1,
    box_size=2,
    border=2
)
qr.add_data("https://xkcd.com/{}/".format(metadata.get("num")))
qr.make(fit=True)
qr_image = qr.make_image(fill_color="black", back_color="white")
qr_w, qr_h = qr_image.size
qr_x = width - qr_w - FOOTER_MARGIN
qr_y = height - qr_h - FOOTER_MARGIN - 20

text_x = FOOTER_MARGIN
text_y = qr_y

output_image = Image.new("RGB", (width, height), color=(255, 255, 255))

draw = ImageDraw.Draw(output_image)

output_image.paste(image, (o_x, o_y, o_x + w, o_y + h))
output_image.paste(qr_image, (qr_x, qr_y, qr_x + w, qr_y + h))

text = metadata.get("alt")

text_in_rect(draw, text, font, (0, 0, 0), (text_x, text_y, qr_x - FOOTER_MARGIN, text_y + qr_h), line_spacing=1.1)
text_in_rect(draw, "xkcd.com", font, (0, 0, 0), (qr_x, qr_y + qr_h, qr_x + qr_w, qr_y + qr_h + 20))

dimensions = ""
if (width, height) != (DEFAULT_WIDTH, DEFAULT_HEIGHT):
    dimensions = f"-{width}x{height}"

output_image.save(f"{OUTPUT_DIR}/xkcd{dimensions}-{suffix}.jpg")