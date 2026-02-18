# WebsiteScreenshot

Captures website screenshots on an interval and sends each image to a Discord webhook.

## Features
- Headless Chromium screenshots via Playwright
- Optional webhook persistence in `data/webhook.txt`
- Repeating interval capture loop
- Automatic retry path after runtime exceptions

## Requirements
- Python 3.10+

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
python websitescreenshot.py <site_url> [--webhook_url <url>] [--interval <seconds>]
```

Example:

```bash
python websitescreenshot.py https://example.com --webhook_url https://discord.com/api/webhooks/... --interval 60
```

## Output
- Temporary screenshots are created in `screenshots/` and sent to the webhook.
- Saved webhook (if provided): `data/webhook.txt`
