import requests
import os
import argparse
import sqlite3
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from winotify import *
badges = []
cursor = None

def notification(directory,badges):
    icon_path = os.path.join(os.path.dirname(__file__), "assets","icon.png")
    toast = Notification(app_id="Roblox Badge Dumper",title=f"""{"✅Badge Dump Complete!✅" if badges>0 else "❌Badge Dump Incomplete!❌"}""",msg= f"""Badges Dumped: {badges}\nInventory Status: {'Private' if badges==0 else 'Public'}""",icon=icon_path)
    toast.set_audio(audio.Reminder, loop=False)
    toast.add_actions(label="Open Folder",launch=str(directory))
    toast.show()

#------------------------------------------------------------
def parse():
    parser = argparse.ArgumentParser(description="CLI tool for checking a users badges. Output in .txt file")
    parser.add_argument("username", type=str,help="Username to check")
    parser.add_argument("output",type=int,help="Way to output (0=txt file, 1=db file),",nargs='?',default=0)
    return parser.parse_args()
parser = parse()
#------------------------------------------------------------
main_path = os.path.dirname(os.path.abspath(__file__))
output_directory = os.path.join(main_path, "user_scrapes")
user_directory = os.path.join(output_directory, parser.username)

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
badge_url = f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100&sortOrder=Asc"
#------------------------------------------------------------
while True:
    url = badge_url
    if cursor:
        url+=f"&cursor={cursor}"
    request = session.get(url,timeout=15)
    fetched_json = request.json()
    badges.extend(fetched_json["data"])
    cursor = fetched_json.get("nextPageCursor")
    if not cursor:
        print("Finished")
        break
#------------------------------------------------------------
if parser.output == 0:
    # TXT OUTPUT
    with open(os.path.join(user_directory, "badges.txt"), "w", encoding="utf-8") as f:
        for badge in badges:
            link = f"https://www.roblox.com/badges/{badge['id']}/"
            json.dump(badge, f, ensure_ascii=False)
    print(f"Text file updated with {len(badges)} badges.")
    print(f"File located at {user_directory}")
    notification(user_directory,len(badges))
else:
    database_directory = os.path.join(user_directory, "badges.db")
    conn = sqlite3.connect(database_directory)
    cursor_db = conn.cursor()
    cursor_db.execute('''
    CREATE TABLE IF NOT EXISTS badges (name TEXT, website_link TEXT,id INTEGER PRIMARY KEY)''')
    conn.commit()

    for badge in badges:
        link = f"https://www.roblox.com/badges/{badge['id']}/"
        cursor_db.execute("INSERT OR IGNORE INTO badges (name, website_link, id) VALUES (?, ?, ?)", (badge['name'], link, badge['id']))
    conn.commit()
    cursor_db.execute("SELECT COUNT(*) FROM badges")
    total_badges = cursor_db.fetchone()[0]

    print(f"Database updated. Total badges in DB: {total_badges}")
    print(f"File located at {user_directory}")
    notification(user_directory,total_badges)
    conn.close()

#------------------------------------------------------------




