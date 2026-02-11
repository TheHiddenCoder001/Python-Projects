import requests
import os
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import time
import argparse

screenshots_path = os.path.join(os.path.dirname(__file__), "screenshots")
data_path = os.path.join(os.path.dirname(__file__), "data")

for p in [screenshots_path,data_path]:
    if not os.path.exists(p):
        os.makedirs(p)

def get_args():
    parser = argparse.ArgumentParser(description="CLI tool website screenshotting")
    parser.add_argument("site_url", type=str, help="URL to screenshot")
    parser.add_argument("--webhook_url",type=str,help="URL of the webhook.")
    parser.add_argument("--interval",type=str,help=f"Interval in seconds.\nDo not spam the API with low intervals or it would result in a shadow ban/rate limiting.",nargs='?',default=60)
    return parser.parse_args()




def get_webhook(input_webhook):
    file = os.path.join(data_path,"webhook.txt")
    
    if input_webhook:
        content=  input_webhook.strip()
        with open(file,"w") as f:
            f.write(content)
            return content
    else:  
        if os.path.exists(file):
            with open(file,"r") as f:
                content = f.read().strip()
                return content
    print("Error: No webhook provided and no saved webhook found.")
    print("Usage: python script.py <url> --webhook <url>")
    exit(1)


def send_discord_message(url,path,message=""):
    with open(path, "rb") as f:
            files = {"file": (path, f, "image/png")}
            payload = {"content":message}
            requests.post(url, files=files,data=payload)
            f.close()


with sync_playwright() as p:
    args = get_args()
    wurl = get_webhook(args.webhook_url)
    surl = args.site_url
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(surl)
    while True:
        try:
            currtime = time.strftime("%d %B %Y at %I:%M %p")    

            image_path = os.path.join(screenshots_path, f'screenshot{len(os.listdir(screenshots_path))+1}.png')
            page.wait_for_load_state("domcontentloaded")
            page.screenshot(path=image_path, full_page=False)
            send_discord_message(wurl,image_path,f"Screenshot on {currtime}")
            time.sleep(0.5)
            os.remove(image_path)
            time.sleep(args.interval)
        except Exception as e:
            print(e)
            browser.close()
            time.sleep(10)
            new_browser = p.chromium.launch(headless=True)
            page = new_browser.new_page()
            page.goto(surl)
            continue