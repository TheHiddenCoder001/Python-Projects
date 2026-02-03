from playwright.sync_api import sync_playwright, TimeoutError
import os
import re
from urllib.parse import urljoin
import requests
from concurrent.futures import ThreadPoolExecutor
import threading
dumppath = os.path.join(os.path.dirname(__file__), "dumps")

def safe_filename(title: str, max_length: int = 150) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", title)
    name = re.sub(r"\s+", " ", name).strip()
    name = name.rstrip(". ")
    if not name:
        name = "file"
    if len(name) > max_length:
        name = name[:max_length].rstrip()
    return name

def download_image(url,folder,name):
    r = requests.get(url)
    r.raise_for_status()
    ext = os.path.splitext(url)[1].split("?")[0]
    if not ext:
        ext = ".jpg"
    path = os.path.join(folder, name + ext)
    with open(path, "wb") as f:
        f.write(r.content)


with sync_playwright() as p:
    URL = "https://scp-wiki.wikidot.com/scp-123"
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    print("OG URL: ", page.url)
    while True:
        # try:
            imglist = []
            title = page.locator("#page-title").text_content().strip()
            content = page.locator("#page-content").text_content().strip()
            imgs = page.locator("#page-content img")
            for i in range(imgs.count()):
                src = imgs.nth(i).get_attribute("src")
                if src:
                    imglist.append(src)
            
            print(imglist)
            
            nav = page.locator("div.footer-wikiwalk-nav >> xpath=.//p[last()]//a[starts-with(@href,'/scp-')]")            
            
            count = nav.count()
            
            pref,num = title.lower().split("-")[0],title.lower().split("-")[1]
            
            if count<2:
                print("over")
                nextscp = "/"+pref+"-"+str(int(num)+1)
            
            else:
                nextscp = nav.nth(1).get_attribute("href")
            
            scppath = os.path.join(dumppath,title)
            img_dir = os.path.join(scppath, "images")
            os.makedirs(img_dir, exist_ok=True)
            with open (os.path.join(scppath, f"{safe_filename(title)}.txt"), "w", encoding="utf-8") as f:
                f.write(f"{title}\n{content}")
                for idx,img in enumerate(imglist):
                    download_image(img,img_dir,safe_filename(title)+"_"+str(idx))
            
            url = f"https://scp-wiki.wikidot.com{nextscp}"
            
            page.goto(url, wait_until="domcontentloaded")
            
            print(f"New URL {url}")
        
        # except Exception as e:
        #     print("exception: ", e)
        #     page.wait_for_timeout(500215)
