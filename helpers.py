import argparse
import io
import re
import requests
from functools import wraps

from PIL import Image

API_ENDPOINT = "https://api.e-hentai.org/api.php"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) " \
             "AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/76.0.3809.100 Safari/537.36"
try_times = 5
parser = argparse.ArgumentParser(
    description="Download galleries from E-Hentai/ExHentai and export them in PDF format."
)


def parse_args():
    global try_times
    parser.add_argument("gallery", metavar="1425378/b6b405e7eb", help="Gallery ID & its token.")
    parser.add_argument("-i", "--member-id", help="Your member ID from your cookies.")
    parser.add_argument("-p", "--pass-hash", help="Your password hash from your cookies.")
    parser.add_argument("-e", "--export-images", help="Save downloaded images.", action="store_true")
    parser.add_argument("-r", "--raw-images", help="Download original if available.", action="store_true")
    parser.add_argument("-w", "--worker", metavar="4", help="Maximum worker number.", type=int, default=4)
    parser.add_argument("-t", "--try-times", metavar="5", help="Maximum try times for each page.", default=5, type=int)
    parser.add_argument(
        "-s", "--source", choices=['e-hentai', 'exhentai'], default="e-hentai",
        help="Where to download. ExHentai requires a valid account."
    )
    args = parser.parse_args()
    if args.worker < 1:
        parser.error("Worker number must be at least 1.")
    if args.try_times < 1:
        parser.error("Try times must be at least 1.")
    if args.source == "exhentai" and not all((args.member_id, args.pass_hash)):
        parser.error("MEMBER_ID and PASS_HASH must be specified to download galleries from ExHentai.")
    if args.raw_images and not all((args.member_id, args.pass_hash)):
        parser.error("MEMBER_ID and PASS_HASH must be specified to download raw images.")
    gallery = re.search(r"(\d+)/(\w+)", args.gallery)
    if not gallery:
        parser.error("Not seem like a valid gallery.")
    gid, token = gallery.group().split("/")
    args.gid = gid
    args.token = token
    return args


def retry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tried = 0
        while tried < try_times:
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                tried += 1
                print(f"{func.__name__} failed ({tried}/{try_times}): {str(e)}")
            else:
                return result
        raise e

    return wrapper


@retry
def get_gallery_metadata(gid, token, with_namespace=True):
    resp = requests.post(API_ENDPOINT, headers={"User-Agent": USER_AGENT}, json={
        "method": "gdata",
        "gidlist": [
            [int(gid), str(token)]
        ],
        "namespace": int(with_namespace)
    })
    return resp.json()["gmetadata"][0]


def remove_transparency(image, bg_colour=(255, 255, 255)):
    im = Image.open(io.BytesIO(image))
    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert("RGBA").split()[-1]
        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        img_bytes = io.BytesIO()
        bg.convert("RGB").save(img_bytes, format="PNG")
        return img_bytes.getvalue()
    else:
        return image
