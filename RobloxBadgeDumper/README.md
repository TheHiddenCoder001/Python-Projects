# RobloxBadgeDumper

Retrieves public Roblox badges for a username and exports results to CSV or SQLite.

## Features
- Resolves username to user ID via Roblox Users API
- Fetches badges with pagination support
- CSV export (`badges.csv`) or SQLite export (`badges.db`)
- Retry-enabled HTTP session
- Progress bars for fetch and save operations
- Completion notification (Windows)

## Requirements
- Python 3.9+
- Windows (notification support)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python robloxbadgedumper.py <username> [csv|db]
```

Examples:

```bash
python robloxbadgedumper.py Builderman csv
python robloxbadgedumper.py Builderman db
```

## Output
- Directory: `user_scrapes/<username>/`
- CSV mode: `badges.csv`
- DB mode: `badges.db`

## Notes
- Private inventories can return zero badges.
- Banned users are detected and reported.
