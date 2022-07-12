# Feed2Image

A repository of tools for converting complicated APIs into simple images for display on embedded, internet-connected devices.

## xkcd2jpg

Convert the daily xkcd (or any given number) to a .jpg image formatted to 600x448 for Inky Frame.

Includes a QR Code linking to the image, and the alt text below.

Daily:

```
python3 xkcd2jpg.py
```

Specific XKCD:

```
python3 xkcd2jpg.py <number>
```
