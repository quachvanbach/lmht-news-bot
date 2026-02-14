import requests
from bs4 import BeautifulSoup
import time
import os

# --- CẤU HÌNH ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1472328723351994439/A3TArsbx6fyEG4LtxX33IK6znyHpgzd-Ngev2DyPS34-VLjanx3b-m3kIhMNDefJJuG2"
URL_NEWS = "https://lienminh.vnggames.com/vi-vn/news/"
FILE_PATH = "last-post.txt"  # Tên file lưu tiêu đề bài viết cuối cùng


def get_last_saved_title():
    """Đọc tiêu đề bài viết cuối cùng từ file"""
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def save_last_title(title):
    """Lưu tiêu đề bài viết mới nhất vào file"""
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write(title)


def send_to_discord(title, link, description):
    """Gửi thông báo định dạng Embed đến Discord"""
    payload = {
        "embeds": [
            {
                "title": title,
                "url": link,
                "description": description,
                "color": 15844367,
                "footer": {"text": "Auto update • Created by Kevin Quach"},
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"✅ Đã gửi Discord thành công: {title}")
        else:
            print(f"❌ Lỗi gửi Discord ({response.status_code})")
    except Exception as e:
        print(f"⚠️ Không thể kết nối đến Discord: {e}")


def check_news():
    # Lấy tiêu đề đã lưu từ file trước khi bắt đầu check
    last_saved_title = get_last_saved_title()

    print(f"[{time.strftime('%H:%M:%S')}] Đang kiểm tra bài viết mới...")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        response = requests.get(URL_NEWS, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title_element = soup.find('div', attrs={"data-testid": "card-title"})
        desc_element = soup.find('div', attrs={"data-testid": "card-description"})

        if title_element:
            current_title = title_element.get_text().strip()
            current_desc = desc_element.get_text().strip() if desc_element else "Không có mô tả chi tiết."

            parent_a = title_element.find_parent('a')
            link = parent_a['href'] if parent_a else URL_NEWS
            if link.startswith('/'):
                link = "https://lienminh.vnggames.com" + link

            # SO SÁNH VỚI DỮ LIỆU TRONG FILE
            if current_title != last_saved_title:
                send_to_discord(current_title, link, current_desc)
                # CẬP NHẬT FILE NGAY LẬP TỨC
                save_last_title(current_title)
                print(f"📌 Bài mới nhất đã được lưu: {current_title}")
            else:
                print("💤 Không có bài viết nào mới.")
        else:
            print("❌ Không tìm thấy phần tử 'card-title'.")

    except Exception as e:
        print(f"⚠️ Lỗi khi quét dữ liệu: {e}")


if __name__ == "__main__":
    print("🚀 BOT TIN TỨC LMHT ĐANG KIỂM TRA...")
    check_news()
