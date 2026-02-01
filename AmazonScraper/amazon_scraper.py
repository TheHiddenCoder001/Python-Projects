import requests
import argparse
import tkinter
import time
from pathlib import Path
from bs4 import BeautifulSoup 
import json
import sys


#-----------------------------------------------------------------------------------------------
if getattr(sys, 'frozen', False):
    bd = Path(sys.executable).parent
else:
    bd = Path(__file__).resolve().parent
od = bd / "scrapes"
od.mkdir(exist_ok=True)
runtime = time.strftime("%d_%m_%Y$%H_%M_%S")
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


products = []
seen_asins = set()
total_searched =0
pages_searched = 0
#-----------------------------------------------------------------------------------------------
def parseargs():
    parser = argparse.ArgumentParser(description="Amazon Scraper")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("max_pages", type=int, help="Maximum number of pages to scrape. Default: unlimited/amazon limits",nargs='?',default=999)
    parser.add_argument("region",type=str,help="Region to scrape. Default: us",nargs='?',default="us")
    return parser.parse_args()

args = parseargs()
original_query = args.query
original_pages = args.max_pages
reg = args.region.lower()
if reg not in AMAZON_DOMAINS:
    print("Invalid region. Choose from:", ", ".join(AMAZON_DOMAINS.keys()))
    sys.exit(1)
domain = AMAZON_DOMAINS[reg]
final_query = original_query.replace(" ", "+").strip() 
url = f"https://www.{domain}/s?k={final_query}"   
#-----------------------------------------------------------------------------------------------
def analyse(url,products):
    session = requests.Session()
    session.headers.update(custom_headers)
    global total_searched
    global pages_searched
    while True:
        response = session.get(url, timeout=15)
        if response.status_code==200:
            if "Robot Check" in response.text:
                print("Blocked by Amazon.")
                break
            if pages_searched >= original_pages:
                break
            
            soup = BeautifulSoup(response.content, "html.parser")
            itemlist = soup.find_all("div", {"data-component-type": "s-search-result"})
            next_tag = soup.select_one("a.s-pagination-next")
            currlen = len(itemlist)
            total_searched += currlen
            pages_searched+=1
            print(f"NUMBER OF ITEMS FOUND - {currlen}")
            print(f"TOTAL ITEMS SCANNED - {total_searched}")
            print(f"PAGE NUMBER - {pages_searched}")
            for item in itemlist:
                try:
                    name_tag =item.find("h2")
                    name = name_tag.text.strip() if name_tag else "N/A"
                    price_tag = item.select_one("span.a-price-whole")
                    price_point = item.select_one("span.a-price-symbol")
                    p1 =price_point.text.strip() if price_point else "N/A"
                    p2 = price_tag.text.strip() if price_tag else "N/A"
                    asin = item.get("data-asin")
                    if not asin or asin in seen_asins:
                        continue
                    seen_asins.add(asin)

                    price = f"{p1}{p2}"
                    rating_tag =item.select_one(".a-icon-alt")
                    rating = rating_tag.text.strip() if rating_tag else "N/A"
                    produrl1 = None
                    produrl0 = item.find("h2")
                    if produrl0:
                        produrl1 = produrl0.find_parent("a")
                    if not produrl1:
                        produrl1 = item.select_one("a[href*='/dp/']")
                    product_url = produrl1.get("href") if produrl1 else None
                    if product_url and product_url.startswith("http"):
                        link = product_url
                    else:
                        link = f"https://www.{domain}{product_url}"
                    products.append({
                "name": name,
                "price": price,
                "rating": rating,
                "link": link,
                })  
                except Exception as e:
                    print("Exception",e)
                    continue
            
            if next_tag:
                next_page = next_tag.get("href")
                if next_page.startswith("http"):
                    new_url = next_page
                else:
                    new_url = f"https://www.{domain}{next_page}"
                url = new_url
                print("NEXT PAGE:", new_url)
            else:
                print("NO NEXT PAGE")
                break

def output(od, runtime, final_query, products, total_searched):
    rtf1 = runtime.split("$")
    date,time = rtf1[0],rtf1[1] 
    runtime_formatted= date.replace("_","/")+" "+time.replace("_",":")
    with open(od / f"{AMAZON_REGIONS[reg]}_{final_query}_{runtime}.txt", "a", encoding="utf-8") as f:
        f.write(f"#query={final_query}\n#region={args.region}\n#totalsearched={total_searched}\n#pagessearched={pages_searched}\n#runtime={runtime_formatted}\n")
        if not products:
            f.write("No products found.\n")
        else:
            json.dump(products, f, ensure_ascii=False, indent=2)
#-----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    analyse(url,products)
    output(od, runtime, final_query, products, total_searched)
    print(f"FILE PATH LOCATED AT - {od / f'products_{final_query}_{runtime}.txt'}")

#-----------------------------------------------------------------------------------------------
