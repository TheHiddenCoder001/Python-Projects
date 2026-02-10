import requests,argparse,sqlite3,time,json,sys,re,os
from pathlib import Path
from bs4 import BeautifulSoup 
from winotify import Notification,audio

#-----------------------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    bd = Path(sys.executable).parent
else:
    bd = Path(__file__).resolve().parent
original_directory = bd / "scrapes"
datab = bd / "prices.db"
original_directory.mkdir(exist_ok=True)
connection = sqlite3.connect(datab)
cursor = connection.cursor()
runtime = time.strftime("%d_%m_%Y$%H_%M_%S")
def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            asin TEXT PRIMARY KEY,
            name TEXT,
            link TEXT,
            first_seen TEXT,
            region TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asin TEXT,
            price INTEGER,
            rating TEXT,
            timestamp TEXT,
            query TEXT,
            region TEXT,
            FOREIGN KEY (asin) REFERENCES products(asin)
        )
    """)

    connection.commit()

init_db()
custom_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}
AMAZON_DOMAINS = {
    "us": "amazon.com",
    "ca": "amazon.ca",
    "mx": "amazon.com.mx",
    "br": "amazon.com.br",
    "uk": "amazon.co.uk",
    "de": "amazon.de",
    "fr": "amazon.fr",
    "it": "amazon.it",
    "es": "amazon.es",
    "nl": "amazon.nl",
    "se": "amazon.se",
    "pl": "amazon.pl",
    "be": "amazon.com.be",
    "ie": "amazon.ie",
    "tr": "amazon.com.tr",
    "in": "amazon.in",
    "jp": "amazon.co.jp",
    "au": "amazon.com.au",
    "sg": "amazon.sg",
    "ae": "amazon.ae",
    "sa": "amazon.sa",
}
AMAZON_REGIONS = {
    "us": "United_States",
    "ca": "Canada",
    "mx": "Mexico",
    "br": "Brazil",

    "uk": "United_Kingdom",
    "de": "Germany",
    "fr": "France",
    "it": "Italy",
    "es": "Spain",
    "nl": "Netherlands",
    "se": "Sweden",
    "pl": "Poland",
    "be": "Belgium",
    "ie": "Ireland",
    "tr": "Turkey",

    "in": "India",
    "jp": "Japan",
    "au": "Australia",
    "sg": "Singapore",
    "ae": "United_Arab_Emirates",
    "sa": "Saudi_Arabia",
}
PRODUCT_LIST = []
SEEN_ASINS = set()
TOTAL_SEARCHED =0
PAGES_SEARCHED = 0
#-----------------------------------------------------------------------------------------------
def parseargs():
    parser = argparse.ArgumentParser(description="Amazon Scraper")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("max_pages", type=int, help="Maximum number of pages to scrape. Default: unlimited/amazon limits",nargs='?',default=999)
    parser.add_argument("region",type=str,help="Region to scrape. Default: us",nargs='?',default="in")
    return parser.parse_args()
args = parseargs()
FIRSTQUERY = args.query
MAXPAGES = args.max_pages
REGION = args.region.lower()
if REGION not in AMAZON_DOMAINS:
    print("Invalid region. Choose from:", ", ".join(AMAZON_DOMAINS.keys()))
    sys.exit(1)
DOMAIN = AMAZON_DOMAINS[REGION]
FINAL_QUERY = FIRSTQUERY.replace(" ", "+").strip() 
URL = f"https://www.{DOMAIN}/s?k={FINAL_QUERY}"   
#-----------------------------------------------------------------------------------------------
def analyse(url,products):
    session = requests.Session()
    session.headers.update(custom_headers)
    global TOTAL_SEARCHED
    global PAGES_SEARCHED
    while True:
        response = session.get(url, timeout=15)
        if response.status_code==200:
            if "Robot Check" in response.text:
                print("Blocked by Amazon.")
                break
            if PAGES_SEARCHED >= MAXPAGES:
                break
            
            soup = BeautifulSoup(response.content, "html.parser")
            web_items = soup.find_all("div", {"data-component-type": "s-search-result"})
            next_page_tag = soup.select_one("a.s-pagination-next")
            web_items_len = len(web_items)
            TOTAL_SEARCHED += web_items_len
            PAGES_SEARCHED+=1
            print(f"NUMBER OF ITEMS FOUND - {web_items_len}")
            print(f"TOTAL ITEMS SCANNED - {TOTAL_SEARCHED}")
            print(f"PAGE NUMBER - {PAGES_SEARCHED}")
            for item in web_items:
                try:
                    link = None 
                    name_tag =item.find("h2")
                    name = name_tag.text.strip() if name_tag else "N/A"
                    
                    price_tag = item.select_one("span.a-price-whole")
                    price_symbol = item.select_one("span.a-price-symbol")
                    
                    symbol =price_symbol.text.strip() if price_symbol else "N/A"
                    amount = price_tag.text.strip() if price_tag else "N/A"
                    price = f"{symbol}{amount}"
                    if amount and amount != "N/A":
                        clean = re.sub(r"[^\d]", "", amount)
                        price_num = int(clean) if clean else None
                    else:
                        price_num = None
                    
                    asin_id = item.get("data-asin")
                    if not asin_id or asin_id in SEEN_ASINS:
                        continue
                    SEEN_ASINS.add(asin_id)
                    
                    rating_tag =item.select_one(".a-icon-alt")
                    rating = rating_tag.text.strip() if rating_tag else "N/A"

                    
                    url_h2_parent = None
                    url_h2_tag = item.find("h2")
                    if url_h2_tag:
                        url_h2_parent = url_h2_tag.find_parent("a")
                    
                    if not url_h2_parent:
                        url_h2_parent = item.select_one("a[href*='/dp/']")
                    final_url = url_h2_parent.get("href") if url_h2_parent else None
                    if final_url and final_url.startswith("http"):
                        link = final_url
                    elif final_url:
                        link = f"https://www.{DOMAIN}{final_url}"
                    cursor.execute("""INSERT OR IGNORE INTO products (asin, name, link, first_seen, region) VALUES (?, ?, ?, ?, ?)""", (asin_id,name,link,runtime,REGION))

                    cursor.execute("""INSERT INTO price_history (asin,price,rating,timestamp,query,region) VALUES (?, ?, ?, ?, ?, ?)""", (asin_id,price_num,rating,runtime,FIRSTQUERY,REGION))

                    products.append({
                "name": name,
                "price": price,
                "rating": rating,
                "link": link,
                })  
                except Exception as e:
                    print("Exception",e)
                    continue
            connection.commit()

            if next_page_tag:
                next_page = next_page_tag.get("href")
                if next_page.startswith("http"):
                    next_page_url = next_page
                else:
                    next_page_url = f"https://www.{DOMAIN}{next_page}"
                url = next_page_url
                print("NEXT PAGE:", next_page_url)
            else:
                print("NO NEXT PAGE")
                break

def output(output_directory, runtime, final_query, products, total_searched):
    rtf1 = runtime.split("$")
    date,time = rtf1[0],rtf1[1] 
    runtime_formatted= date.replace("_","/")+" "+time.replace("_",":")
    with open(output_directory / f"{AMAZON_REGIONS[REGION]}_{final_query}_{runtime}.txt", "a", encoding="utf-8") as f:
        f.write(f"#query={final_query}\n#region={args.region}\n#totalsearched={total_searched}\n#pagessearched={PAGES_SEARCHED}\n#runtime={runtime_formatted}\n")
        if not products:
            f.write("No products found.\n")
        else:
            json.dump(products, f, ensure_ascii=False, indent=2)
    
#-----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    analyse(URL,PRODUCT_LIST)
    output(original_directory, runtime, FINAL_QUERY, PRODUCT_LIST, TOTAL_SEARCHED)
    connection.close()
    filepath = original_directory / f'products_{FINAL_QUERY}_{runtime}.txt'
    print(f"FILE PATH LOCATED AT - {original_directory / f'products_{FINAL_QUERY}_{runtime}.txt'}")
    
    toast = Notification(app_id="Amazon Scraper",title="Amazon Scraper",msg="Amazon Scrape Complete!",icon=r"c:\path\to\icon.png")
    toast.set_audio(audio.Mail, loop=False)
    toast.add_actions(label="Open File",launch=str(filepath))
    toast.show()
    print(filepath)
    print(filepath.exists())
    os.startfile(filepath)

#-----------------------------------------------------------------------------------------------
