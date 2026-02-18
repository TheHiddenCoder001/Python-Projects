# SCPWikiDumper

Downloads SCP Wiki entries and related page images for a numeric range.

## Features
- Iterates from a start SCP number to an end SCP number
- Saves page title/content into text files
- Downloads images in parallel using a thread pool
- Completion notification (Windows)

## Requirements
- Python 3.10+
- Windows (notification support)

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
python SCPWikiDumper.py <start> <end>
```

Example:

```bash
python SCPWikiDumper.py 1 10
```

## Output
- Dump root: `dumps/`
- Per-page folder: `dumps/<SCP title>/`
- Text file: `<safe_title>.txt`
- Images: `images/`
