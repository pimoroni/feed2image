import requests
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import Roboto
import qrcode
import math
import sys
import random


TARGET_WIDTH = 600
TARGET_HEIGHT = 448
FOOTER_MARGIN = 10
OUTPUT_DIR = "build"
JOKES = "https://raw.githubusercontent.com/Sv443/JokeAPI/master/data/jokes/regular/jokes-en.json"


font = ImageFont.truetype(Roboto, 50)


def text_in_rect(canvas, text, font, color, rect, align='left', valign='top', line_spacing=1.1):
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

    # Given a rectangle, reflow and scale text to fit, centred
    while font.size > 0:
        space_width = font.getsize(" ")[0]
        line_height = int(font.size * line_spacing)
        max_lines = math.floor(height / line_height)
        lines = []

        # Determine if text can fit at current scale.

        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            words = paragraph.split(" ")
            while len(lines) < max_lines and len(words) > 0:
                line = []

                while len(words) > 0 and font.getsize(" ".join(line + [words[0]]))[0] <= width:
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


jokes = requests.get(JOKES).json()

if jokes["info"]["formatVersion"] != 3:
    raise RuntimeError("Unrecognised jokes format!")

# Select safe jokes
jokes = [joke for joke in jokes["jokes"] if joke.get("safe", False) == True]

# Pick 24 jokes at random
jokes = random.sample(jokes, 24)

print(jokes)


def mkqrcode(text):
    qr = qrcode.QRCode(
        version=1,
        box_size=2,
        border=2
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def render_twopart(image, joke):
    draw = ImageDraw.Draw(image)

    setup = joke.get("setup")
    delivery = joke.get("delivery")

    section_height = int((TARGET_HEIGHT - 100 - FOOTER_MARGIN) / 2)
    text_in_rect(draw, setup, font, (255, 0, 0), (FOOTER_MARGIN, FOOTER_MARGIN, TARGET_WIDTH - FOOTER_MARGIN, FOOTER_MARGIN + section_height))

    text_in_rect(draw, delivery, font, (0, 0, 255), (FOOTER_MARGIN, FOOTER_MARGIN + section_height, TARGET_WIDTH - FOOTER_MARGIN, section_height + section_height))


def render_onepart(image, joke):
    draw = ImageDraw.Draw(image)

    text = joke.get("joke").replace("\n", "\n\n")

    text_in_rect(draw, text, font, (255, 0, 0), (FOOTER_MARGIN, FOOTER_MARGIN, TARGET_WIDTH - FOOTER_MARGIN, TARGET_HEIGHT - 100))


def render_common(image, joke):
    draw = ImageDraw.Draw(image)

    qr_image = mkqrcode("https://jokeapi.dev/")
    qr_w, qr_h = qr_image.size
    qr_x = TARGET_WIDTH - qr_w - FOOTER_MARGIN
    qr_y = TARGET_HEIGHT - qr_h - FOOTER_MARGIN - 20

    image.paste(qr_image, (qr_x, qr_y))

    text_in_rect(draw, "jokeapi.dev", font, (0, 0, 0), (qr_x, qr_y + qr_h, qr_x + qr_w, qr_y + qr_h + 20))


for hour, joke in enumerate(jokes):
    twopart = joke.get("type") == "twopart"

    output_image = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), color=(255, 255, 255))

    if twopart:
        render_twopart(output_image, joke)
    else:
        render_onepart(output_image, joke)

    render_common(output_image, joke)

    output_image.save(f"{OUTPUT_DIR}/jokeapi-joke-of-the-hour-{hour}.jpg", optimize=True, quality=70)
