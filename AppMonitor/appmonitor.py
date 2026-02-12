import threading,sys,psutil,time,random,os,pyautogui,logging 
from winotify import Notification,audio
from pystray import Icon, MenuItem as item
from PIL import Image
import win32gui
import win32con
import win32com.client

quotes = [
    "You have power over your mind — not outside events. Realize this, and you will find strength.",
    "He who has a why to live can bear almost any how.",
    "Absorb what is useful, discard what is not, add what is uniquely your own.",
    "In the midst of chaos, there is also opportunity.",
    "Discipline is choosing between what you want now and what you want most.",
    "Life is like riding a bicycle. To keep your balance, you must keep moving.",
    "Luck is what happens when preparation meets opportunity.",
    "Victory belongs to the most persevering."
]

videos = os.path.join(os.path.dirname(__file__),"assets","videos")
logs = os.path.join(os.path.join(os.path.dirname(__file__),"logs"))
for thing in [videos,logs]:
    if not os.path.exists(thing):
        os.mkdir(thing)

logging.basicConfig(filename=os.path.join(logs,"logs.txt"), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main(target):
    target_list = target.split(" ")
    video_files = [f for f in os.listdir(videos) if os.path.isfile(os.path.join(videos, f))]
    try:
        logging.info(f"Program was ran, with parameters {target}") 
        running = True
        paused = threading.Event()
        paused.set()
        def monitor_loop():
            nonlocal running
            while running:
                paused.wait()
                kill()
                time.sleep(0.5)
        
        def notification(target_name,sendQuote=True):
            vid = os.path.join(videos,random.choice(video_files))
            def run_video(vid_path):
                    os.startfile(vid_path)
                    logging.info(f"{vid_path} was played.")
                    time.sleep(0.5)
                    hwnd = win32gui.FindWindow(None, vid_path)
                    if hwnd:
                            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                            shell = win32com.client.Dispatch("WScript.Shell")
                            shell.sendkeys("%")
                            win32gui.SetForegroundWindow(hwnd)
                            logging.info("vlc focused")
                            time.sleep(1.5)
                            pyautogui.hotkey("ctrl","h")
            run_video(vid)

        def kill():
            nonlocal running
            for process in psutil.process_iter(["name","pid"]):
                try:
                    name = process.info["name"].lower()
                    if any(target in name for target in target_list if target):
                        for child in process.children(recursive=True):
                            child.kill()
                        process.kill()
                        logging.info(f"Program {name} was killed.")
                        notification({name},True)
                except psutil.NoSuchProcess:
                    logging.error("Error")
                    pass
        
        def pause(icon,item):
            paused.clear()
            icon.notify("Paused", "Monitoring stopped")
            logging.info("Program was paused.")

        def start(icon,item):
            paused.set()
            icon.notify("Started", "Monitoring started")
            logging.info("Program was started.")

        def quit(icon,item):
            nonlocal running
            icon.stop()
            logging.info("Program was exited.")
            sys.exit()

        def setup_tray():
            nonlocal running
            img = Image.open(os.path.join(os.path.dirname(__file__), 'assets', 'icon.png'))
            menu = (item("Pause", pause),item("Start", start),item("Exit", quit))
            icon = Icon("AppMonitor", img, "App Monitor", menu)
            thread = threading.Thread(target=monitor_loop, daemon=True)
            thread.start()
            icon.run()


        setup_tray()
    except Exception as e:
        logging.error("Error:",e)
        logging.error("Type:",type(e))

if __name__ == "__main__":
    main("roblox gorebox minecraft")



