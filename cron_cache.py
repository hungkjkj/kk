import time
from datetime import datetime, timedelta
import quant_screener

def run_cache():
    sectors = ["Ngân hàng", "Bán lẻ", "Công nghệ thông tin", "Xây dựng và Vật liệu"]
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Bắt đầu tiến trình tạo cache tự động cho các ngành: {sectors}...")
    for s in sectors:
        print(f"  -> Đang cache dữ liệu ngành: {s}...")
        try:
            quant_screener.run_screener_for_sector(s)
            print(f"  -> Xong {s}. Nghỉ 60 giây để tránh Rate Limit...")
            time.sleep(60)
        except Exception as e:
            print(f"  -> Lỗi khi cache {s}: {e}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Tiến trình tạo cache hoàn tất.")

def main():
    print("Khởi động Cron Cache...")
    run_cache()
    print("Đã chạy xong! Script sẽ thoát. (Thích hợp chạy qua Render Cron Job hoặc Windows Task Scheduler)")

if __name__ == "__main__":
    main()
