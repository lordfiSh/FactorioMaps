"""What a tile is written as, in one place.

The extension used to be spelled out in zoom.py, in ref.py and again in
web/index.js, with a fourth copy hardcoded in a renderbox url. Selecting a format
means all four have to agree, so they are derived from here instead.

This is deliberately a leaf module: zoom.py loads libturbojpeg at import time, so
having ref.py import from it would drag that into every cross-referencing worker
for no reason.
"""
from collections import namedtuple

# Factorio writes screenshots as png and take_screenshot offers no other lossless
# option, so this is not configurable. The thumbnail follows web/index.html's
# og:image, which names it explicitly.
SOURCEEXT = ".png"
THUMBNAILEXT = ".png"


TileFormat = namedtuple("TileFormat", ("name", "ext", "defaultQuality", "compareThreshold"))


# compareThreshold is the number ref.py multiplies by the tile's pixel count to
# decide whether two tiles differ. It has to sit above the noise the codec adds
# to an unchanged tile, or every tile looks changed and nothing is ever deduped,
# and below a real change, or a changed tile is dropped and the viewer serves a
# stale one from an older snapshot. It is therefore per codec, and measured:
# across 120 real tiles the median noise is 4749 for jpeg at quality 80 and 12661
# for webp at 75, both against a tile count of 512**2. jpeg's long standing .03
# leaves 8-11% of unchanged tiles wrongly kept; .08 puts webp at the same rate.
# defaultQuality is per format because the numbers are not comparable across
# codecs — they index each encoder's own scale. webp at 80 is roughly jpeg at 85,
# so pairing the two at one number asks webp for better output and is paid for in
# bytes: measured over the same tiles, webp 80 is 10% larger than jpeg 80. webp 75
# is the match — 92% of jpeg 80's size at a better PSNR, 32.57 against 31.82.
FORMATS = {
    "jpg": TileFormat(name="jpg", ext=".jpg", defaultQuality=80, compareThreshold=.03),
    "webp": TileFormat(name="webp", ext=".webp", defaultQuality=75, compareThreshold=.08),
}

DEFAULTFORMAT = "jpg"


def getFormat(name: str) -> TileFormat:
    try:
        return FORMATS[name]
    except KeyError:
        raise ValueError(f"unknown tile format '{name}', expected one of {', '.join(FORMATS)}")
