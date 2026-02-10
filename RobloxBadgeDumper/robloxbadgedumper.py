import requests
import os
import argparse
import sqlite3
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from winotify import *
from tqdm import tqdm
badges = []
cursor = None

def notification(directory,badges,isbanned=False,username=None):
    icon_path = os.path.join(os.path.dirname(__file__), "assets","icon.png")
    if isbanned:
            toast = Notification(app_id="Roblox Badge Dumper",title=f"""{"❌Badge Dump Incomplete!❌"}""",msg=f"""Account Has Been Terminated""" ,icon=icon_path)
    else:
        toast = Notification(app_id="Roblox Badge Dumper",title=f"""{"✅Badge Dump Complete!✅" if badges>0 else "❌Badge Dump Incomplete!❌"}""",msg= f"""Name = {username}\nBadges Dumped: {badges}\n{"Inventory Status: Private" if badges==0 else "Inventory Status: Public" if badges>0 else"Error Occured"}""",icon=icon_path)
    toast.set_audio(audio.Mail, loop=False)
    toast.add_actions(label="Open Folder",launch=str(directory))
    toast.show()

#------------------------------------------------------------
def parse():
    parser = argparse.ArgumentParser(description="CLI tool for checking a users badges. Output in .txt file (0)/ .db file (1)")
    parser.add_argument("username", type=str,help="Username to check")
    parser.add_argument("output",type=int,help="Way to output (0=txt file, 1=db file),",nargs='?',default=0)
    return parser.parse_args()
parser = parse()
#------------------------------------------------------------
main_path = os.path.dirname(os.path.abspath(__file__))
output_directory = os.path.join(main_path, "user_scrapes")
user_directory = os.path.join(output_directory, parser.username)
database_directory = os.path.join(user_directory, "badges.db")

#------------------------------------------------------------
session = requests.session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})
retry = Retry(total=5, backoff_factor=1,status_forcelist=[429,500, 502, 503, 504],allowed_methods=['GET', 'POST'])
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
session.mount("http://", adapter)
username = parser.username
output = parser.output
request = session.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False},timeout=15)
data = request.json()
if not data['data']:
    print("User not found")
    exit()
if not os.path.exists(user_directory):
    os.makedirs(user_directory)
user_id = data["data"][0]["id"]
user_info = session.get(f"https://users.roblox.com/v1/users/{user_id}").json()
name= user_info.get('name')
if user_info.get("isBanned"):
    notification(user_directory,0,True,name)
    exit()
badge_url = f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100&sortOrder=Asc"
#------------------------------------------------------------
pbar = tqdm(desc="Fetching Badges",unit=" badges")
while True:
    url = badge_url
    if cursor:
        url+=f"&cursor={cursor}"
    request = session.get(url,timeout=15)
    fetched_json = request.json()
    badges.extend(fetched_json["data"])
    pbar.update(len(fetched_json["data"]))
    cursor = fetched_json.get("nextPageCursor")
    if not cursor:
        print("Finished")
        pbar.close()
        break
#------------------------------------------------------------
if parser.output == 0:
    if len(badges)==0:
        notification(user_directory,len(badges))
        exit()
    else:
        with open(os.path.join(user_directory, "badges.txt"), "w", encoding="utf-8") as f:
            for badge in tqdm(badges, desc="Writing text file"):
                link = f"https://www.roblox.com/badges/{badge['id']}/"
                json.dump(badge, f, ensure_ascii=False)
        print(f"Text file updated with {len(badges)} badges.")
        print(f"File located at {user_directory}")
        notification(user_directory,len(badges),False,name)
else:
    if len(badges)==0:
                notification(user_directory,len(badges),False,name)
                exit()
    else:
        conn = sqlite3.connect(database_directory)
        cursor_db = conn.cursor()
        cursor_db.execute('''
        CREATE TABLE IF NOT EXISTS badges (name TEXT, website_link TEXT,id INTEGER PRIMARY KEY)''')
        conn.commit()
        for badge in tqdm(badges, desc="Saving to database"):
                    link = f"https://www.roblox.com/badges/{badge['id']}/"
                    cursor_db.execute("INSERT OR IGNORE INTO badges (name, website_link, id) VALUES (?, ?, ?)", (badge['name'], link, badge['id']))
        conn.commit()
        cursor_db.execute("SELECT COUNT(*) FROM badges")
        total_badges = cursor_db.fetchone()[0]

        print(f"Database updated. Total badges in DB: {total_badges}")
        print(f"File located at {user_directory}")
        notification(user_directory,len(badges),False,name)
        conn.close()

#------------------------------------------------------------




