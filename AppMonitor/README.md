# AppMonitor

A Python-based tool that **monitors specific applications**, **terminates them if detected**, and **plays a motivational video**.

---

## Features

### Main Application

#### Monitoring
- On first run, creates directories for logs and video assets.
- Continuously monitors for applications matching predefined names.

#### Processing
- If a monitored application is detected:
  - Terminates the full process tree.
  - Plays a motivational video using the system’s default media player.

#### Logging
- Logs every detection and video playback event.
- Enables debugging by tracking timestamps of actions.

---

## Taskbar Controls

- **Pause**  
  Pauses monitoring and logs the action.

- **Start**  
  Resumes monitoring and logs the action.

- **Stop**  
  Terminates the program and logs the action.  
  > The program must be restarted manually after stopping.

---

## Usage

Run the script:

```bash
python appmonitor.py
