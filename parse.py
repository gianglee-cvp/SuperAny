import re
from bs4 import BeautifulSoup
import csv

with open('test.html', 'r', encoding='utf-8') as f:
    html = f.read()

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

# Sử dụng utf-8-sig để Excel mở không bị lỗi font tiếng Việt
with open('results.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(f, fieldnames=['title', 'price', 'sales', 'star', 'link'])
    writer.writeheader()
    writer.writerows(results)

for idx, r in enumerate(results, 1):
    print(f"{idx}. {r['title']}")
    print(f"   Giá: {r['price']} | Bán: {r['sales']} | Đánh giá: {r['star']} sao")
    print(f"   Link: {r['link']}\n")
