import re
import requests
from bs4 import BeautifulSoup

from helpers import USER_AGENT, retry

GALLERY_PAGE_URL = "https://{}.org/g/{}/{}/?p={}"
PAGE_LINK_PATTERN = re.compile(r"https://(e-hentai|exhentai)\.org/s/.+")
RAW_IMAGE_LINK_PATTERN = re.compile(r"https://(e-hentai|exhentai)\.org/fullimg\.php\?.+")

session = requests.session()


@retry
def get_page_links(gid, token, file_count, source="e-hentai", member_id=None, pass_hash=None):
    links = []
    current_page = 0
    while len(links) < file_count:
        url = GALLERY_PAGE_URL.format(source, gid, token, current_page)
        resp = session.get(url, timeout=30, headers={
            "Cookie": f"ipb_member_id={member_id}; ipb_pass_hash={pass_hash}",
            "User-Agent": USER_AGENT
        })
        soup = BeautifulSoup(resp.content, "html.parser")
        for tag in soup.find_all("a", href=True):
            if PAGE_LINK_PATTERN.match(tag["href"]):
                links.append(tag["href"])
        current_page += 1
    return links


@retry
def get_image(url, member_id=None, pass_hash=None, raw_image=False):
    cookie = f"ipb_member_id={member_id}; ipb_pass_hash={pass_hash}"
    page_resp = session.get(url, timeout=30, headers={
        "Cookie": cookie,
        "User-Agent": USER_AGENT
    })
    cookie = ""
    soup = BeautifulSoup(page_resp.content, "html.parser")
    image_element = soup.find("img", {"id": "img"})
    image_url = image_element["src"]
    if raw_image:
        for tag in soup.find_all("a", href=True):
            if RAW_IMAGE_LINK_PATTERN.match(tag["href"]):
                image_url = tag["href"]
                cookie = f"ipb_member_id={member_id}; ipb_pass_hash={pass_hash}"
                break
    image_resp = session.get(image_url, timeout=30, headers={
        "Cookie": cookie,
        "User-Agent": USER_AGENT
    })
    return image_resp.content
