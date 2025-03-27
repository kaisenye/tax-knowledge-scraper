# crawl_irs_sitemap_pdfs.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import xml.etree.ElementTree as ET
import time
import os

SITEMAP_URL = "https://www.irs.gov/sitemap.xml"
DOMAIN = "https://www.irs.gov"

def fetch_sitemap_urls(sitemap_url):
    print("Fetching sitemap...")
    res = requests.get(sitemap_url)
    tree = ET.fromstring(res.content)
    urls = [url.text for url in tree.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    return urls

def extract_pdf_links_from_page(page_url):
    try:
        res = requests.get(page_url, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        pdfs = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.lower().endswith('.pdf'):
                full_url = urljoin(page_url, href)
                pdfs.append(full_url)
        return pdfs
    except Exception as e:
        print(f"Error fetching {page_url}: {e}")
        return []

def crawl_irs_for_pdfs():
    all_pdfs = set()
    visited_pages = 0

    urls = fetch_sitemap_urls(SITEMAP_URL)
    print(f"Found {len(urls)} pages in sitemap")

    for url in tqdm(urls, desc="Crawling IRS pages"):
        pdf_links = extract_pdf_links_from_page(url)
        all_pdfs.update(pdf_links)
        visited_pages += 1
        time.sleep(0.2)  # be polite

    print(f"\nVisited {visited_pages} pages.")
    print(f"Found {len(all_pdfs)} unique PDFs.")

    os.makedirs("output", exist_ok=True)
    with open("output/irs_pdf_links.txt", "w") as f:
        for link in sorted(all_pdfs):
            f.write(link + "\n")

    print("Saved to output/irs_pdf_links.txt")

if __name__ == "__main__":
    crawl_irs_for_pdfs()
