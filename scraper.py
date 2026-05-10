import sys
import csv
import time
import os
import re
import subprocess
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright

def launch_chrome():
    print("[*] Đang tự động mở Google Chrome...")
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = r"C:\chrome_debug_profile"
    subprocess.Popen([
        chrome_path,
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}"
    ])
    time.sleep(3) # Đợi Chrome khởi động

def scrape_1688(keyword):
    print(f"[*] Bắt đầu tìm kiếm: {keyword}")
    
    with sync_playwright() as p:
        print("[*] Đang kết nối tới trình duyệt Chrome hiện tại...")
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            # Nếu chưa mở, tự động mở Chrome rồi thử lại
            launch_chrome()
            try:
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
            except Exception as e:
                print("[-] LỖI: Không thể tự động mở hoặc kết nối tới Chrome.")
                return

        # Lấy trang hiện tại (trang đầu tiên)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        
        if keyword.startswith("http"):
            search_url = keyword
        else:
            encoded_keyword = quote_plus(keyword)
            # URL đã bao gồm tham số sắp xếp theo lượng bán (sortType=va_sales360) và ép kiểu utf8
            search_url = f"https://s.1688.com/selloffer/offer_search.htm?keywords={encoded_keyword}&sortType=va_sales360&descendOrder=true&charset=utf8"
        
        print(f"[*] Đang truy cập trang web: {search_url}")
        page.goto(search_url)
        try:
            page.wait_for_load_state('domcontentloaded', timeout=15000)
        except Exception:
            pass # Bỏ qua lỗi timeout nếu trang load quá chậm do tracking ngầm
        
        print("[*] Đang chờ trang load xong. Nếu có mã CAPTCHA hoặc yêu cầu đăng nhập, bạn có thể thao tác tay ngay trên cửa sổ trình duyệt...")
        # Đợi 15 giây để trang ổn định, hoặc để bạn kịp giải quyết CAPTCHA / Đăng nhập
        time.sleep(15)
        
        print("[*] Đang cuộn trang để load đủ sản phẩm...")
        # Scroll từ từ xuống để hình ảnh và dữ liệu load (1688 dùng lazy load)
        for _ in range(5):
            page.mouse.wheel(0, 1000)
            time.sleep(1)
            
        print("[*] Đang tiến hành phân tích HTML để lấy top 20 sản phẩm...")
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        products = soup.find_all('a', class_='i18n-card-wrap')
        
        results = []
        for p in products[:20]:
            title_el = p.select_one('.offer-title')
            title = re.sub(r'\s+', ' ', title_el.text).strip() if title_el else 'N/A'
            
            number_el = p.select_one('.price-wrap .number')
            unit_el = p.select_one('.price-wrap .unit')
            
            number = number_el.text.strip() if number_el else ''
            unit = unit_el.text.strip() if unit_el else ''
            price = number + unit if number else 'N/A'
            
            sales_el = p.select_one('.sale-amount-wrap')
            sales = sales_el.text.strip() if sales_el else 'N/A'
            
            star_el = p.select_one('.star-level-wrap .star-level-text')
            star = star_el.text.strip() if star_el else 'N/A'
            
            link = p.get('href', 'N/A')
            
            results.append({
                'title': title,
                'price': price,
                'sales': sales,
                'star': star,
                'link': link
            })
        
        if not results:
            print("[-] Không tìm thấy sản phẩm nào! Có thể do:")
            print(" 1. Trang web yêu cầu đăng nhập/xác minh CAPTCHA.")
            print(" 2. Selector HTML đã thay đổi (1688 thường xuyên đổi giao diện).")
        else:
            # Lưu ra file CSV
            csv_file = "results1.csv"
            keys = ['title', 'price', 'sales', 'star', 'link']
            # Sử dụng utf-8-sig để Excel mở không bị lỗi font
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as output_file:
                dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(results)
            
            print(f"\\n[+] Đã lưu top {len(results)} sản phẩm vào file '{csv_file}'.\\n")
            
            # In ra màn hình
            for idx, p in enumerate(results, 1):
                print(f"{idx}. {p['title']}")
                print(f"   Giá: {p['price']} | Bán: {p['sales']} | Đánh giá: {p['star']} sao")
                print(f"   Link: {p['link']}\\n")
                
        # Đóng kết nối tới trình duyệt
        browser.disconnect()

if __name__ == "__main__":
    # Ghép tất cả các tham số truyền vào thành một từ khóa (để không cần gõ ngoặc kép)
    if len(sys.argv) > 1:
        kw = " ".join(sys.argv[1:])
    else:
        kw = "áo thun nam" # Mặc định nếu không nhập gì
    scrape_1688(kw)
