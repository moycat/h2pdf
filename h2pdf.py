#!/usr/bin/env python3
import img2pdf
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from spider import get_image, get_page_links
from helpers import get_gallery_metadata, parse_args, remove_transparency

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
    _get_image = partial(get_image, member_id=args.member_id, pass_hash=args.pass_hash, raw_image=args.raw_images)
    with ThreadPoolExecutor(max_workers=args.worker) as executor:
        future = executor.map(_get_image, page_links)
        for page, image in enumerate(future, 1):
            images.append(image)
            if args.export_images:
                with open(image_path + "/" + str(page) + ".jpg", "wb") as f:
                    f.write(image)

    with open(ROOT + "/galleries/" + gallery["title"] + ".pdf", "wb") as file:
        file.write(img2pdf.convert([remove_transparency(image) for image in images]))


if __name__ == "__main__":
    main()
