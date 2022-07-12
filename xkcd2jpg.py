import requests
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import Roboto
import qrcode
import math
import sys

TARGET_WIDTH = 600
TARGET_HEIGHT = 448


font = ImageFont.truetype(Roboto, 18)


def text_in_rect(canvas, text, font, color, rect, align='left', line_spacing=1.1):
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

    # Given a rectangle, reflow and scale text to fit, centred
    while font.size > 0:
        space_width = font.getsize(" ")[0]
        line_height = int(font.size * line_spacing)
        max_lines = math.floor(height / line_height)
        lines = []

        # Determine if text can fit at current scale.
        words = text.split(" ")

        while len(lines) < max_lines and len(words) > 0:
            line = []

            while len(words) > 0 and font.getsize(" ".join(line + [words[0]]))[0] <= width:
                line.append(words.pop(0))

            lines.append(" ".join(line))

        if len(lines) <= max_lines and len(words) == 0:
            # Solution is found, render the text.
            y = int(rect[1] + (height / 2) - (len(lines) * line_height / 2) - (line_height - font.size) / 2)

            bounds = [rect[2], y, rect[0], y + len(lines) * line_height]

            for line in lines:
                line_width = font.getsize(line)[0]
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


try:
    number = int(sys.argv[1])
    metadata = requests.get(f"https://xkcd.com/{number}/info.0.json").json()
    suffix = str(number)

except (IndexError, ValueError):
    metadata = requests.get("https://xkcd.com/2641/info.0.json").json()
    suffix = "daily"

response = requests.get(metadata.get("img"), stream=True)

image = Image.open(response.raw)
w, h = image.size
ratio = min(TARGET_WIDTH / w, (TARGET_HEIGHT - 100) / h)

if ratio < 1.0:
    w = int(w * ratio)
    h = int(h * ratio)

    image = image.resize((w, h))

o_x = int((TARGET_WIDTH - w) / 2)
o_y = int((TARGET_HEIGHT - 100 - h) / 2)

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
qr_x = (TARGET_WIDTH - 100) + int((100 - qr_w) / 2)
qr_y = (TARGET_HEIGHT - 100) + int((100 - qr_h) / 2)

output_image = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), color=(255, 255, 255))

draw = ImageDraw.Draw(output_image)

output_image.paste(image, (o_x, o_y))
output_image.paste(qr_image, (qr_x, qr_y))

text_in_rect(draw, metadata.get("alt"), font, (0, 0, 0), (0, TARGET_HEIGHT - 100, TARGET_WIDTH - 100, TARGET_HEIGHT), line_spacing=1.1)

output_image.save(f"xkcd2bin-{suffix}.jpg")