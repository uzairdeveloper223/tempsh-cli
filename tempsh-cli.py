#!/usr/bin/env python3

import sys
import os
import requests
from pathlib import Path
import time

VERSION = "1.0.0"
UPLOAD_URL = "https://temp.sh/upload"

def format_size(bytes):
    for unit in ['b', 'kb', 'mb', 'gb']:
        if bytes < 1024.0:
            return f"{bytes:.1f}{unit}"
        bytes /= 1024.0
    return f"{bytes:.1f}tb"

def progress_bar(current, total, width=50):
    if total == 0:
        return ""
    
    percent = current / total
    filled = int(width * percent)
    bar = '=' * filled + '-' * (width - filled)
    return f"[{bar}] {percent*100:.1f}%"

class UploadProgress:
    def __init__(self, total_size):
        self.total = total_size
        self.uploaded = 0
        self.start_time = time.time()
        self.last_update = 0
    
    def update(self, chunk_size):
        self.uploaded += chunk_size
        current_time = time.time()
        if current_time - self.last_update >= 0.1 or self.uploaded >= self.total:
            elapsed = current_time - self.start_time
            if elapsed > 0:
                speed = self.uploaded / elapsed
                speed_str = f"{format_size(speed)}/s"
            else:
                speed_str = "calculating..."
            
            progress = progress_bar(self.uploaded, self.total)
            uploaded_str = format_size(self.uploaded)
            total_str = format_size(self.total)
            
            print(f"\r{progress} {uploaded_str}/{total_str} @ {speed_str}", end='', flush=True)
            self.last_update = current_time

def upload_file(filepath):
    if not os.path.exists(filepath):
        print(f"error: file not found: {filepath}")
        return False
    
    file_size = os.path.getsize(filepath)
    if file_size > 4 * 1024 * 1024 * 1024:
        print("error: file too large (max 4gb)")
        return False
    
    filename = Path(filepath).name
    print(f"uploading {filename} ({format_size(file_size)})...")
    
    try:
        progress = UploadProgress(file_size)
        from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
        
        with open(filepath, 'rb') as f:
            encoder = MultipartEncoder(fields={'file': (filename, f, 'application/octet-stream')})
            monitor = MultipartEncoderMonitor(encoder, lambda m: progress.update(m.bytes_read - progress.uploaded))
            
            response = requests.post(
                UPLOAD_URL,
                data=monitor,
                headers={'Content-Type': monitor.content_type},
                timeout=300
            )
        
        print()
        if response.status_code == 200:
            url = response.text.strip()
            print(f"success!")
            print(f"url: {url}")
            print(f"expires: 3 days")
            return True
        else:
            print(f"error: upload failed (status {response.status_code})")
            return False
    except ImportError:
        print("note: install requests-toolbelt for progress bar")
        print("  pip install requests-toolbelt")
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f)}
            response = requests.post(UPLOAD_URL, files=files, timeout=300)
        
        if response.status_code == 200:
            url = response.text.strip()
            print(f"success!")
            print(f"url: {url}")
            print(f"expires: 3 days")
            return True
        else:
            print(f"error: upload failed (status {response.status_code})")
            return False
    except Exception as e:
        print(f"\nerror: {str(e)}")
        return False

def upload_stdin():
    print("reading from stdin (ctrl+d to end)...")
    try:
        data = sys.stdin.buffer.read()
        if not data:
            print("error: no data received")
            return False
        
        print(f"uploading {len(data)} bytes...")
        files = {'file': ('stdin.txt', data)}
        response = requests.post(UPLOAD_URL, files=files, timeout=300)
        
        if response.status_code == 200:
            url = response.text.strip()
            print(f"\nsuccess!")
            print(f"url: {url}")
            print(f"expires: 3 days")
            return True
        else:
            print(f"error: upload failed (status {response.status_code})")
            return False
    except Exception as e:
        print(f"error: {str(e)}")
        return False

def show_help():
    help_text = f"""tempsh-cli v{VERSION} - temporary file upload tool

usage:
  tempsh-cli <file>              upload a file
  cat file | tempsh-cli          upload from stdin
  tempsh-cli -h                  show this help
  tempsh-cli -v                  show version

examples:
  tempsh-cli document.pdf
  echo "hello world" | tempsh-cli
  cat image.png | tempsh-cli

powered by temp.sh
files expire after 3 days | max size 4gb
"""
    print(help_text)

def main():
    try:
        import requests
    except ImportError:
        print("error: requests module not found")
        print("install: pip install requests")
        sys.exit(1)
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ['-h', '--help', 'help']:
            show_help()
            sys.exit(0)
        elif arg in ['-v', '--version', 'version']:
            print(f"tempsh-cli v{VERSION}")
            sys.exit(0)
        else:
            success = upload_file(arg)
            sys.exit(0 if success else 1)
    else:
        if not sys.stdin.isatty():
            success = upload_stdin()
            sys.exit(0 if success else 1)
        else:
            show_help()
            sys.exit(0)

if __name__ == "__main__":
    main()
