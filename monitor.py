import json, os, hashlib
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 15

def _get(url):
    return requests.get(url, headers=HEADERS, timeout=TIMEOUT).text

def fetch_govcn():
    items = []
    html = _get("https://www.gov.cn/zhengce/zuixin.htm")
    soup = BeautifulSoup(html, 'html.parser')
    for li in soup.select('ul.list_zuixin li'):
        a = li.find('a')
        if not a: continue
        title = a.get_text(strip=True)
        link = "https://www.gov.cn" + a['href']
        date_span = li.find('span', class_='date')
        date_str = date_span.get_text(strip=True) if date_span else ""
        items.append({"dept": "中国政府网/国务院", "title": title, "url": link, "date_raw": date_str})
    return items

def fetch_csrc():
    items = []
    html = _get("https://www.csrc.gov.cn")
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.select('div.news_box a'):
        title = a.get_text(strip=True)
        if not title: continue
        link = "https://www.csrc.gov.cn" + a['href']
        items.append({"dept": "证监会", "title": title, "url": link, "date_raw": ""})
    return items

def fetch_ndrc():
    items = []
    html = _get("https://www.ndrc.gov.cn/xwdt/xwfb/")
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.select('.u-list li a'):
        title = a.get_text(strip=True)
        if not title: continue
        link = "https://www.ndrc.gov.cn" + a['href']
        items.append({"dept": "发改委", "title": title, "url": link, "date_raw": ""})
    return items

def fetch_miit():
    items = []
    html = _get("https://www.miit.gov.cn/zwgk/zcwj/wjfb/index.html")
    soup = BeautifulSoup(html, 'html.parser')
    for a in soup.select('.cl-list li a'):
        title = a.get_text(strip=True)
        if not title: continue
        link = "https://www.miit.gov.cn" + a['href']
        items.append({"dept": "工信部", "title": title, "url": link, "date_raw": ""})
    return items

def send_to_wechat(token, content):
    url = "http://www.pushplus.plus/send"
    data = {"token": token, "title": "四大部门政策早报", "content": content}
    requests.post(url, json=data)

def main():
    token = os.getenv("PUSHPLUS_TOKEN")
    if not token:
        print("No Token Found!")
        return

    all_items = fetch_govcn() + fetch_csrc() + fetch_ndrc() + fetch_miit()
    
    # 简单去重
    seen = set()
    unique_items = []
    for item in all_items:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique_items.append(item)

    # 组装消息
    msg_lines = ["📋 **四大部门政策早报**\n"]
    for item in unique_items[:15]: # 最多发15条
        msg_lines.append(f"**[{item['dept']}]** {item['title']}\n🔗 {item['url']}\n")
    
    send_to_wechat(token, "\n".join(msg_lines))

if __name__ == "__main__":
    main()
