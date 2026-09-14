import os
import re
import json
import time
import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup

# Ensure UTF-8 output on Windows console
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

RAW_HTML_PATH = r"C:\Users\user\.gemini\antigravity-ide\brain\07f270d5-6a56-4f0d-9809-b189b1ba6cfb\scratch\raw_aarti_list.html"
OUTPUT_JSON_PATH = r"d:\SOFTWARES\xampp82new\htdocs\androidapps\arti\src\assets\data\webdunia_arties_raw.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'hi,en-US;q=0.9,en;q=0.8',
    'Referer': 'https://hindi.webdunia.com/dharma/aarti'
}

def safe_url(url):
    try:
        parts = urllib.parse.urlsplit(url)
        path = urllib.parse.quote(parts.path)
        return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))
    except Exception:
        return url

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'[\r\t]+', ' ', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def parse_aarti_page(url, fallback_title="", fallback_img=""):
    try:
        req_url = safe_url(url)
        r = requests.get(req_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None
        
        soup = BeautifulSoup(r.content.decode('utf-8', 'ignore'), 'html.parser')
        article = soup.find(class_=lambda c: c and 'article_in_content' in c)
        if not article:
            return None
        
        # 1. Main High-Res Image
        main_img = ""
        # Often the main article image is in .arti_img img or first big img inside article
        for img in article.find_all('img'):
            src = img.get('src') or img.get('data-src') or ""
            if src and 'wd-image.webdunia.com' in src and ('1200x' in src or '720x' in src):
                main_img = src
                break
        
        if not main_img:
            # Check anywhere in page for .arti_img
            for img in soup.select('.arti_img img, .article_detail img'):
                src = img.get('src') or img.get('data-src') or ""
                if src and 'wd-image.webdunia.com' in src and ('1200x' in src or '720x' in src):
                    main_img = src
                    break
        
        if not main_img:
            main_img = fallback_img

        # 2. Extract Title from H1 or fallback
        h1 = soup.find('h1')
        title = clean_text(h1.get_text()) if h1 else fallback_title
        if not title:
            title = fallback_title

        # 3. Clean up non-lyric elements inside article (ads, author box, next article, share)
        for junk in article.select('.article_author_w, .arti_social_block, .next_article_block, script, style, iframe, .ad-box, .arti_share_icons, .also_read, .article_sticky_sect'):
            junk.decompose()

        # 4. Extract paragraphs and meaningful text
        content_paragraphs = []
        for p in article.find_all(['p', 'div', 'h2', 'h3']):
            # skip if parent was already processed or is an ad/share
            cls = ' '.join(p.get('class', []))
            if any(bad in cls for bad in ['share', 'author', 'social', 'adv', 'banner', 'sticky', 'icon']):
                continue
            
            # Format text preserving linebreaks in verses (<br>)
            for br in p.find_all('br'):
                br.replace_with('\n')
                
            txt = p.get_text()
            lines = [clean_text(line) for line in txt.split('\n') if clean_text(line)]
            if lines:
                combined = '\n'.join(lines)
                # Filter out unwanted common phrases
                if any(x in combined for x in ['वेबदुनिया', 'Webdunia', 'कॉपीराइट', 'सर्वाधिकार', 'advertisement', 'WhatsApp']):
                    continue
                if combined not in content_paragraphs:
                    content_paragraphs.append(combined)

        return {
            'url': url,
            'title': title,
            'image': main_img,
            'paragraphs': content_paragraphs
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    if not os.path.exists(RAW_HTML_PATH):
        print(f"Raw HTML not found at {RAW_HTML_PATH}")
        return
    
    with open(RAW_HTML_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    blocks = soup.find_all('aside', class_='db_arti_block')
    
    seen_urls = set()
    extracted_items = []
    
    print(f"Total blocks found in HTML: {len(blocks)}")
    
    for block in blocks:
        a_tag = block.find('a', href=True)
        if not a_tag:
            continue
        
        rel_href = a_tag['href']
        if rel_href.startswith('http'):
            full_url = rel_href
        else:
            full_url = 'https://hindi.webdunia.com' + rel_href
            
        if full_url in seen_urls:
            continue
        seen_urls.add(full_url)
        
        img_tag = block.find('img')
        fallback_img = img_tag.get('src') if img_tag else ""
        fallback_title = (img_tag.get('alt') or img_tag.get('title') or "").strip() if img_tag else ""
        
        h3 = block.find('h3')
        if h3 and h3.get_text(strip=True):
            fallback_title = h3.get_text(strip=True)
            
        extracted_items.append({
            'url': full_url,
            'title': fallback_title,
            'thumbnail': fallback_img
        })

    print(f"Unique Aarti URLs to scrape: {len(extracted_items)}")
    
    results = []
    for i, item in enumerate(extracted_items, 1):
        print(f"[{i}/{len(extracted_items)}] Scraping: {item['url']}")
        data = parse_aarti_page(item['url'], fallback_title=item['title'], fallback_img=item['thumbnail'])
        if data:
            results.append(data)
        time.sleep(0.5) # respectful delay

    os.makedirs(os.path.dirname(OUTPUT_JSON_PATH), exist_ok=True)
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Successfully scraped {len(results)} Aartis and saved to {OUTPUT_JSON_PATH}")

if __name__ == '__main__':
    main()
