# Roblox Badge Dumper / Roblox Badge Scraper

A Python-based command-line utility that retrieves all public badges
owned by a Roblox user and saves them locally for inspection, archival,
and analysis.

This project was created as a hands-on exercise in building real-world
scraping and automation tools, focusing on:

-   REST API consumption\
-   Pagination handling with cursors\
-   CLI argument parsing\
-   Session-based HTTP requests\
-   Filesystem automation\
-   SQLite database persistence\
-   Structured data storage\
-   Automation-friendly scraping workflows\
-   Defensive programming for unreliable networks

It is suitable for learning purposes, data collection experiments, and
personal Roblox account analysis.

------------------------------------------------------------------------

## Overview

Given a Roblox username, the script:

1.  Resolves the username into a Roblox user ID via Roblox's public
    Users API.\
2.  Queries the Roblox Badges API for badge ownership data.\
3.  Iterates through paginated API responses using cursor tokens.\
4.  Collects every badge name and badge ID returned.\
5.  Writes the results to disk.\
6.  Supports two export formats:
    -   Plain-text (`.txt`) files\
    -   SQLite database (`.db`) files

The tool is optimized for command-line usage and batch automation
scenarios.

------------------------------------------------------------------------

## Features

-   Username → user ID resolution\
-   Unlimited badge fetching\
-   Cursor-based pagination\
-   TXT export mode\
-   SQLite database export mode\
-   Duplicate-safe inserts\
-   CLI-first design\
-   Custom User-Agent headers\
-   Fast execution\
-   Offline-friendly storage\
-   Simple relational database schema\
-   Minimal third-party dependencies\
-   Easy integration into scripts and cron jobs\
-   Deterministic output paths\
-   Clear console logging\
-   Lightweight footprint

------------------------------------------------------------------------

## Requirements

-   Python 3.9 or newer\
-   Active internet connection\
-   Access to Roblox public APIs

### Python Dependencies

Install the only required third-party package:

pip install requests

Standard-library modules used include:

-   os\
-   argparse\
-   sqlite3\
-   json

------------------------------------------------------------------------

## Installation

Clone the repository and install dependencies:

git clone https://github.com/yourname/roblox-badge-dumper.git\
cd roblox-badge-dumper\
pip install requests

------------------------------------------------------------------------

## Usage

Run the script directly from a terminal or shell:

python robloxbadgedumper.py `<username>`{=html} \[output\]

------------------------------------------------------------------------

## CLI Arguments

  Argument   Required   Description
  ---------- ---------- -----------------------------------------------
  username   Yes        Roblox username to scan
  output     No         Output mode: 0 = TXT, 1 = SQLite DB (default)

------------------------------------------------------------------------

## Example Commands

TXT export:

python robloxbadgedumper.py Builderman 0

SQLite database export:

python robloxbadgedumper.py Builderman 1

------------------------------------------------------------------------

## Output Formats

### TXT Mode

Creates a file named:

badges.txt

Each line follows this structure:

Badge Name - https://www.roblox.com/badges/`<id>`{=html}/

------------------------------------------------------------------------

### SQLite Mode

Creates a file named:

badges.db

With the following schema:

CREATE TABLE IF NOT EXISTS badges (\
name TEXT,\
website_link TEXT,\
id INTEGER PRIMARY KEY\
);

Duplicate records are avoided using:

INSERT OR IGNORE

------------------------------------------------------------------------

## Error Handling & Behavior

The script is designed to fail safely and predictably:

-   Exits immediately if a username cannot be resolved\
-   Automatically stops when all pages are fetched\
-   Handles pagination cursor changes\
-   Avoids duplicate database records\
-   Prints completion messages and badge counts\
-   Keeps network logic simple for reliability

------------------------------------------------------------------------

## Use Cases

-   Roblox badge archiving\
-   Account history analysis\
-   Badge collectors\
-   Dataset creation\
-   Offline browsing of badge lists\
-   API scraping practice\
-   Automation pipelines\
-   Python CLI portfolio projects\
-   Educational demonstrations\
-   Research tooling

------------------------------------------------------------------------

## Disclaimer

This tool relies on Roblox's public APIs.

-   Intended strictly for educational and personal use\
-   Respect Roblox's Terms of Service\
-   Do not abuse API rate limits\
-   Avoid large-scale scraping without permission

You are responsible for how you use this software.

------------------------------------------------------------------------

## Planned Improvements

Future enhancements may include:

-   JSON export option\
-   CSV export option\
-   Timestamped scans\
-   Progress bars\
-   Retry and exponential backoff logic\
-   Rate-limit handling\
-   Badge metadata enrichment\
-   Multi-user batch scanning\
-   Logging support\
-   Configuration files\
-   Async request handling\
-   Dashboard or UI frontend\
-   Statistics and rarity analysis

------------------------------------------------------------------------

## License

MIT License.

You are free to:

-   Use the software\
-   Modify the code\
-   Redistribute copies\
-   Learn from the implementation\
-   Extend the project

------------------------------------------------------------------------

## Contributing

Contributions are welcome.

Recommended workflow:

1.  Fork the repository\
2.  Create a feature branch\
3.  Make clean, documented commits\
4.  Submit a pull request describing your changes

------------------------------------------------------------------------

## Support

For bugs, questions, or feature requests, open an issue in the project
repository.

# RobloxBadgeDumper

A Python tool for dumping badge data for Roblox users.

## Features
- Fetches and stores badge data for specified Roblox users.
- Outputs data in CSV and SQLite DB formats.
- Organizes user data in `user_scrapes/` by username.

## Usage
- Run `robloxbadgedumper.py` and follow prompts or configure as needed.
- Badge data is saved in `user_scrapes/<username>/`.

## Requirements
- Python 3.x
- Requests (see script for details)

## License
For educational and personal use only.
