import requests
import os
import argparse
import sqlite3
import json
badges = []

def parse():
    parser = argparse.ArgumentParser(description="CLI tool for checking a users badges. Output in .txt file")
    parser.add_argument("username", type=str,help="Username to check")
    parser.add_argument("output",type=int,help="Way to output (0=txt file, 1=db file),",nargs='?',default=1)
    return parser.parse_args()
parser = parse()


main_path = os.path.dirname(os.path.abspath(__file__))
output_directory = os.path.join(main_path, "user_scrapes")
user_directory = os.path.join(output_directory, parser.username)
if not os.path.exists(user_directory):
    os.makedirs(user_directory)


session = requests.session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})


username = parser.username
output = parser.output
cursor = None




request = session.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False})
data = request.json()
if not data['data']:
    print("User not found")
    exit()
user_id = data["data"][0]["id"]
badge_url = f"https://badges.roblox.com/v1/users/{user_id}/badges?limit=100&sortOrder=Asc"



while True:
    url = badge_url
    if cursor:
        url+=f"&cursor={cursor}"
    request = session.get(url)
    fetched_json = request.json()
    badges.extend(fetched_json["data"])
    cursor = fetched_json.get("nextPageCursor")
    if not cursor:
        print("Finished")
        break

if parser.output == 0:
    # TXT OUTPUT
    with open(os.path.join(user_directory, "badges.txt"), "w", encoding="utf-8") as f:
        for badge in badges:
            link = f"https://www.roblox.com/badges/{badge['id']}/"
            f.write(f"{badge['name']} - {link}\n")
    print(f"Text file updated with {len(badges)} badges.")

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
#----------------------------------------
    cursor_db.execute("SELECT COUNT(*) FROM badges")
    print(f"Database updated. Total badges in DB: {cursor_db.fetchone()[0]}")
    conn.close()




