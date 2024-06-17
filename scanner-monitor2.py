import os
import shutil
import logging
import time
import socket
from inotify_simple import INotify, flags
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler


# Get the hostname
hostname = socket.gethostname()

# Define directories based on hostname
if hostname == "Z2":
    scanner_dir = "H:\\My Drive\\Documents\\Scanner"
    paperless_dir = "E:\\SyncThing\\Documents\\paperless\\consume"
    jopin_dir = "H:\\My Drive\\Documents\\Scanner\\joplin"
elif hostname == "bastion":
    scanner_dir = "/mnt/data2024/syncthing/Documents/Scanner"
    paperless_dir = "/mnt/data2024/syncthing/Documents/paperless/consume"
    jopin_dir = "/mnt/data2024/syncthing/Documents/Scanner/joplin"
elif hostname == "Maverick":
    scanner_dir = "H:\\My Drive\\Documents\\Scanner"
    paperless_dir = "E:\\SyncThing\\Documents\\paperless\\consume"
    jopin_dir = "H:\\My Drive\\Documents\\Scanner\\joplin"   
else:
    raise ValueError(f"Hostname '{hostname}' not recognized. Please configure the directories for this hostname.")

# Get the directory where the script is stored
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "scanner_monitor.log")

# Configure logging
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

def process_file(filepath):
    try:
        logging.info(f"Copying file: {filepath}")
        shutil.copy(filepath, paperless_dir)
        shutil.copy(filepath, jopin_dir)
        logging.info(f"Copied {filepath} to {paperless_dir} and {jopin_dir}")
    except Exception as e:
        logging.error(f"Error copying {filepath}: {e}")

def monitor_directory():
    inotify = INotify()
    watch_flags = flags.CREATE | flags.MOVED_TO
    wd = inotify.add_watch(scanner_dir, watch_flags)
    
    logging.info("Starting the file monitor script on hostname: " + hostname)
    while True:
        for event in inotify.read():
            for flag in flags.from_mask(event.mask):
                if flag in (flags.CREATE, flags.MOVED_TO):
                    filepath = os.path.join(scanner_dir, event.name)
                    process_file(filepath)
        time.sleep(1)  # Sleep for a short time to avoid busy waiting

if __name__ == "__main__":
    try:
        monitor_directory()
    except KeyboardInterrupt:
        logging.info("Stopping the file monitor script")