import time
import shutil
import logging
import os
import socket
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


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
    scanner_dir = r"E:\SyncThing\Documents\Scanner"
    paperless_dir = "E:\\SyncThing\\Documents\\paperless\\consume"
    jopin_dir = r"E:\SyncThing\Documents\Scanner\joplin"
else:
    raise ValueError(f"Hostname '{hostname}' not recognized. Please configure the directories for this hostname.")


# Get the directory where the script is stored
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "scanner_monitor.log")
processed_files_file = os.path.join(script_dir, f"processed_files_{hostname}.json")

# Configure logging
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')
logging.info("Starting the file monitor script on hostname: " + hostname)

# Configure logging
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(message)s')

# Load processed files
if os.path.exists(processed_files_file):
    with open(processed_files_file, 'r') as f:
        processed_files = set(json.load(f))
else:
    processed_files = set()

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or event.src_path.endswith('.tmp'):
            return
        else:
            process_file(event.src_path)

    def on_moved(self, event):
        if event.is_directory or event.dest_path.endswith('.tmp'):
            return
        else:
            process_file(event.dest_path)

def save_processed_files():
    with open(processed_files_file, 'w') as f:
        json.dump(list(processed_files), f)

def process_file(filepath):
    if filepath in processed_files or filepath.endswith('.tmp'):
        return

    retries = 3
    for attempt in range(retries):
        try:
            logging.info(f"Copying file: {filepath}")
            shutil.copy(filepath, paperless_dir)
            shutil.copy(filepath, jopin_dir)
            logging.info(f"Copied {filepath} to {paperless_dir} and {jopin_dir}")
            processed_files.add(filepath)
            save_processed_files()
            break  # Exit the loop if the copy was successful
        except PermissionError as e:
            logging.error(f"Permission error copying {filepath}: {e}")
            if attempt < retries - 1:
                logging.info(f"Retrying in 5 seconds... (Attempt {attempt + 1} of {retries})")
                time.sleep(5)
            else:
                logging.error(f"Failed to copy {filepath} after {retries} attempts")
        except Exception as e:
            logging.error(f"Error copying {filepath}: {e}")
            break

def scan_directory():
    for root, dirs, files in os.walk(scanner_dir):
        for file in files:
            filepath = os.path.join(root, file)
            process_file(filepath)

if __name__ == "__main__":
    logging.info("Starting the file monitor script on hostname: " + hostname)
    
    # Initialize the file handler for watchdog
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=scanner_dir, recursive=False)
    observer.start()
    
    try:
        while True:
            scan_directory()
            time.sleep(60)  # Periodic scan every 60 seconds
    except KeyboardInterrupt:
        logging.info("Stopping the file monitor script")
        observer.stop()
    observer.join()
    save_processed_files()  # Save the processed files before exiting