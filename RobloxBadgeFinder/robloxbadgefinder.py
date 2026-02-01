import requests
session = requests.session()

username = "MrMemeus"
badges = []
cursor = None

req = session.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False})

data = req.json()
print(data)
if not data['data']:
    print("User not found")
    exit()
uid = data["data"][0]["id"]
print(uid)
burl = f"https://badges.roblox.com/v1/users/{uid}/badges?limit=100&sortOrder=Asc"

while True:
    url = burl
    if cursor:
        url+=f"&cursor={cursor}"
    r = session.get(url)
    j = r.json()
    print(j)
    badges.extend(j["data"])
    cursor = j.get("nextPageCursor")
    if not cursor:
        print("Finished")
        break

for b in badges:
    print(b["name"], "-", b["id"])