import os
import re
import json
import time
import sys
import requests

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ARTIES_JSON_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\arties.json"
IMAGES_DIR = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\public\assets\images\arties"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def download_and_localize():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    with open(ARTIES_JSON_PATH, 'r', encoding='utf-8') as f:
        arties = json.load(f)
        
    print(f"Total Aartis to process: {len(arties)}")
    
    success_count = 0
    fail_count = 0
    
    for idx, item in enumerate(arties, 1):
        # 1. Remove any webdunia_url field completely
        if 'webdunia_url' in item:
            del item['webdunia_url']
            
        # 2. Sanitize significance text from any source mentions
        if 'significance' in item and 'Webdunia' in item['significance']:
            item['significance'] = f"Sacred traditional Aarti of {item.get('deity', 'Deity')} for devotional pooja."
            
        img_url = item.get('image', '')
        if img_url and img_url.startswith('http'):
            # Determine extension
            ext = '.webp'
            if '.jpg' in img_url.lower() or '.jpeg' in img_url.lower():
                ext = '.jpg'
            elif '.png' in img_url.lower():
                ext = '.png'
                
            file_name = f"{item['id']}{ext}"
            local_file_path = os.path.join(IMAGES_DIR, file_name)
            relative_url = f"/assets/images/arties/{file_name}"
            
            # Download if not already downloaded
            if not os.path.exists(local_file_path) or os.path.getsize(local_file_path) == 0:
                try:
                    print(f"[{idx}/{len(arties)}] Downloading: {item['id']} ...")
                    r = requests.get(img_url, headers=HEADERS, timeout=20)
                    if r.status_code == 200 and len(r.content) > 500:
                        with open(local_file_path, 'wb') as img_f:
                            img_f.write(r.content)
                        item['image'] = relative_url
                        success_count += 1
                    else:
                        print(f"  Warning: Status {r.status_code} for {img_url}")
                        item['image'] = "" # Do not keep external URL
                        fail_count += 1
                    time.sleep(0.15)
                except Exception as e:
                    print(f"  Error downloading {img_url}: {e}")
                    item['image'] = ""
                    fail_count += 1
            else:
                item['image'] = relative_url
                success_count += 1
        else:
            # If empty or not http, keep as is
            pass
            
    # Save localized arties.json
    with open(ARTIES_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(arties, f, ensure_ascii=False, indent=2)
        
    print("\n--- Summary ---")
    print(f"Successfully localized: {success_count} images")
    print(f"Failed / Missing: {fail_count}")
    print(f"Images directory: {IMAGES_DIR}")
    print(f"Saved localized dataset to: {ARTIES_JSON_PATH}")

if __name__ == '__main__':
    download_and_localize()
