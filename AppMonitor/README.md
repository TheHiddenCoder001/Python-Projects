# AppMonitor

Monitors selected processes, kills them when detected, and plays a local video while logging activity.

## Features
- Continuous process monitoring
- Process tree termination
- System tray controls (`Pause`, `Start`, `Exit`)
- Log files for runtime and software events
- Video playback from `assets/videos/`

## Requirements
- Python 3.10+
- Windows

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python appmonitor.py
```

Default targets are hardcoded in `appmonitor.py` (`roblox gorebox minecraft`).

## Output
- Logs: `logs/run.log`, `logs/software.log`
- Videos read from: `assets/videos/`
