import logging
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from threading import Lock
from datetime import datetime
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    )

logger = logging.getLogger(__name__)

failed_archives = []
failed_archives_lock = Lock()

# Add more archive extensions as needed
common_archive_extensions = [
    '.7z', '.zip', '.rar', '.tar', '.gz', '.bz2', '.xz', '.lzma', '.iso', '.dmg', '.img', '.vhd'
    ]


def test_archive(archive_path, passwords):
    result = run_test_proc(archive_path, "")
    if result:
        logger.info(f"No password required for {archive_path}")
        return ""

    for password in passwords:
        result = run_test_proc(archive_path, password)
        if result:
            logger.info(f"Password found for {archive_path}: {password}")
            return password

    logger.error(f"No password found for {archive_path}")
    return None


def run_test_proc(archive_path, password):
    command = ['7z', 't', archive_path, '-p{}'.format(password), '-y']
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, errors='ignore')
    try:
        for line in process.stderr:
            if 'wrong password' in line.lower():
                return False
    finally:
        process.kill()
        process.wait()
    return process.returncode == 0


def extract_archive(archive_path, password):
    archive_name = os.path.splitext(os.path.basename(archive_path))[0]
    extract_dir = os.path.join(os.path.dirname(archive_path), archive_name)
    os.makedirs(extract_dir, exist_ok=True)

    command = ['7z', 'x', archive_path, '-p{}'.format(password), '-o{}'.format(extract_dir), '-aos', '-y']
    result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode == 0:
        logger.info(f"Extracted {archive_path}")
        return True
    else:
        logger.error(f"Failed to extract {archive_path}")
        return False


def process_archive(archive_path, password_list):
    password = test_archive(archive_path, password_list)
    if password is None:
        with failed_archives_lock:
            failed_archives.append(archive_path)
            return

    if not extract_archive(archive_path, password):
        with failed_archives_lock:
            failed_archives.append(archive_path)


def main():
    archive_folder = input("Enter the path to the archive folder: ")
    if not os.path.exists(archive_folder) or not os.path.isdir(archive_folder):
        logger.fatal("Archive folder not found")
        return
    password_list = input("Enter the path to the password list: ")
    if not os.path.exists(password_list) or not os.path.isfile(password_list):
        logger.fatal("Password list not found")
        return
    
    with open(password_list, "r") as f:
        password_list = [password.strip() for password in f.readlines()]

    num_threads = int(input("Enter the number of threads to run: "))
    if num_threads <= 0:
        logger.fatal("Invalid number of threads")
        return

    archives = [f for f in os.listdir(archive_folder) if f.endswith(tuple(common_archive_extensions))]
    archive_paths = [os.path.join(archive_folder, archive) for archive in archives]

    logger.info(f"Found {len(archives)} archives in {archive_folder}")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(process_archive, archive_path, password_list) for archive_path in archive_paths]
        for future in as_completed(futures):
            future.result()

    if failed_archives:
        logger.info("Failed archives:")
        for fail in failed_archives:
            print(fail)


if __name__ == "__main__":
    main()


