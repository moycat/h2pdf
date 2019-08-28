import argparse
import re
import requests

API_ENDPOINT = "https://api.e-hentai.org/api.php"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) " \
              "AppleWebKit/537.36 (KHTML, like Gecko) " \
              "Chrome/76.0.3809.100 Safari/537.36"
parser = argparse.ArgumentParser(
    description="Download galleries from E-Hentai/ExHentai and export them in PDF format."
)


def parse_args():
    parser.add_argument("gallery", metavar="1425378/b6b405e7eb", help="Gallery ID & its token.")
    parser.add_argument("-i", "--member-id", help="Your member ID from your cookies.")
    parser.add_argument("-p", "--pass-hash", help="Your password hash from your cookies.")
    parser.add_argument("-e", "--export-images", help="Save downloaded images.", action="store_true")
    parser.add_argument("-r", "--raw-images", help="Download original if available.", action="store_true")
    parser.add_argument(
        "-s", "--source", choices=['e-hentai', 'exhentai'], default="e-hentai",
        help="Where to download. ExHentai requires a valid account."
    )
    args = parser.parse_args()
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


def get_gallery_metadata(gid, token, with_namespace=True):
    resp = requests.post(API_ENDPOINT, headers={"User-Agent": USER_AGENT}, json={
        "method": "gdata",
        "gidlist": [
            [int(gid), str(token)]
        ],
        "namespace": int(with_namespace)
    })
    return resp.json()["gmetadata"][0]
