import os,requests,re,argparse
from playwright.sync_api import sync_playwright, TimeoutError
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from winotify import Notification,audio
exec = ThreadPoolExecutor(max_workers=10)

def get_args():
    parser = argparse.ArgumentParser(description="SCP Wiki Dumper")
    parser.add_argument("init",type=int,help="Start number of SCP")
    parser.add_argument("final",type=int,help="End number of SCP")
    return parser.parse_args()

def notification(status, scrapes):
    toast = Notification(
        app_id="SCP Wiki Dumper",
        title="SCP Wiki Scraper Feedback",
        msg=f"Scrapes: {scrapes}\nStatus: {status}", # Fixed string formatting
        icon=os.path.join(os.path.dirname(__file__), "assets", "icon.png")
    )
    toast.set_audio(audio.Mail, loop=False)
    toast.show()

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
    r = requests.get(url,timeout=20)
    r.raise_for_status()
    ext = os.path.splitext(url)[1].split("?")[0]
    if not ext:
        ext = ".jpg"
    path = os.path.join(folder, name + ext)
    with open(path, "wb") as f:
        f.write(r.content)
    return f"Finished {name}"


dumppath = os.path.join(os.path.dirname(__file__), "dumps")
os.makedirs(dumppath, exist_ok=True)
args = get_args()

with sync_playwright() as p: #initialize
    init = args.init
    final = args.final + 1
    count_scp = 1
    URL = f"https://scp-wiki.wikidot.com/scp-{init}"
    end_url = f"https://scp-wiki.wikidot.com/scp-{final}"
    #-------------------------------------------------------------------------------------------------------------------------------
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(URL, wait_until="domcontentloaded")
    print("OG URL: ", page.url)
    while True: #per page scope
        try:
            title = page.locator("#page-title").text_content().strip()
            content = page.locator("#page-content").text_content().strip()
            
            images_list = []
            imgs = page.locator("#page-content img")
            
            for i in range(imgs.count()):
                src1 = imgs.nth(i).get_attribute("src")
                src = urljoin(page.url, src1)
                if src:
                    images_list.append(src)
            
            print(images_list)
            
            nav = page.locator("div.footer-wikiwalk-nav >> xpath=.//p[last()]//a[starts-with(@href,'/scp-')]")            
            count = nav.count()
            parts = title.lower().split("-", 1)
            pref = parts[0]
            num = parts[1] if len(parts) > 1 else "0"

            
            if count<2:
                print("encountred some weird shit, working")
                nextscp = "/"+pref+"-"+str(int(num)+1)
                
            
            else:
                nextscp = nav.nth(1).get_attribute("href")
            
            scppath = os.path.join(dumppath,title)
            img_dir = os.path.join(scppath, "images")
            os.makedirs(img_dir, exist_ok=True)
            with open (os.path.join(scppath, f"{safe_filename(title)}.txt"), "w", encoding="utf-8") as f:
                f.write(f"{title}\n{content}")
            for idx,img in enumerate(images_list):
                # download_image(img,img_dir,safe_filename(title)+"_"+str(idx))
                # image_t = threading.Thread(target=download_image, args=(img,img_dir,f"{safe_filename(title)}_{idx}"))
                f = exec.submit(download_image, img, img_dir, f"{safe_filename(title)}_{idx}")            
                f.add_done_callback(lambda f: print(f.result()))
            
            url = f"https://scp-wiki.wikidot.com{nextscp}"
            if url == end_url:
                notification("Complete",count_scp)
                browser.close()
                break
            else:
                page.goto(url, wait_until="domcontentloaded")
                count_scp+=1
                print(f"New URL {url}")
            
        
        except Exception as e:
            print("exception: ", e)
            notification("Error",count_scp)
            browser.close()
            break