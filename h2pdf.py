#!/usr/bin/env python3
import img2pdf
import os

from spider import get_image, get_page_links
from helpers import get_gallery_metadata, parse_args

ROOT = os.path.dirname(os.path.realpath(__file__))


def main():
    args = parse_args()

    print("Getting metadata of gallery...")
    gallery = get_gallery_metadata(args.gid, args.token)

    image_path = ROOT + "/images/" + gallery["title"]
    if args.export_images and not os.path.exists(image_path):
        os.mkdir(image_path)

    print("Getting", gallery["filecount"], "page links...")
    page_links = get_page_links(
        args.gid, args.token, int(gallery["filecount"]), args.source, args.member_id, args.pass_hash
    )

    print("Getting images...")
    images = []
    for page, link in enumerate(page_links, 1):
        image = get_image(link, args.member_id, args.pass_hash, args.raw_images)
        images.append(image)
        if args.export_images:
            with open(image_path + "/" + str(page) + ".jpg", "wb") as f:
                f.write(image)

    with open(ROOT + "/galleries/" + gallery["title"] + ".pdf", "wb") as file:
        file.write(img2pdf.convert(images))


if __name__ == "__main__":
    main()
