import sys
import time
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def debug_1688():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        Stealth().apply_stealth_sync(page)
        
        search_url = "https://s.1688.com/selloffer/offer_search.htm?keywords=Th%E1%BB%9Di+trang+tr%E1%BA%BB+em&spm=a260k.home2025.searchbox.0&charset=utf8&sortType=va_sales360&descendOrder=true&beginPage=1"
        page.goto(search_url)
        page.wait_for_load_state('networkidle')
        time.sleep(5)
        
        html = page.content()
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(html)
        browser.close()

if __name__ == "__main__":
    debug_1688()
