import threading,sys,psutil,time,random,os
from winotify import Notification,audio
from pystray import Icon, MenuItem as item
from pystray import Icon
from PIL import Image


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





def main(target):
    target_list = target.split(" ")
    try:
        print("Running now...")
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
            toast = Notification(app_id="App Monitor",title="Is this really where you want to be?",msg=f"""You tried opening {target_name}\n{random.choice(quotes) if sendQuote else "" }""",icon=f"{os.path.join(os.path.dirname(__file__), 'assets', 'icon.png')}")
            toast.set_audio(audio.Mail, loop=False)
            print(toast.script)
            toast.show()

        def kill():
            nonlocal running
            for process in psutil.process_iter(["name","pid"]):
                try:
                    name = process.info["name"].lower()
                    if any(target in name for target in target_list if target):
                        for child in process.children(recursive=True):
                            child.kill()
                        process.kill()
                        print(f"fuck of noob, no {name} for you")
                        notification({name},True)
                except psutil.NoSuchProcess:
                    print("Error")
                    pass
        
        def pause(icon,item):
            paused.clear()
            icon.notify("Paused", "Monitoring stopped")

        def start(icon,item):
            paused.set()
            icon.notify("Started", "Monitoring started")
        def quit(icon,item):
            nonlocal running
            icon.stop()
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
        print("Error:",e)
        print("Type:",type(e))

if __name__ == "__main__":
    main("roblox")



