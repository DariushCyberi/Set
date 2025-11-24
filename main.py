from soroush_api import SoroushClient
import time
import threading
import json
import os

CONFIG_FILE = "config.json"

# ---------------------------
# Load / Save Config
# ---------------------------
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "", "interval": 60}

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

config = load_config()

# ---------------------------
# LOGIN
# ---------------------------
client = SoroushClient(session="session.sor")

if not client.is_logged_in():
    phone = input("شماره را وارد کنید: ")
    client.request_code(phone)

    code = input("کد ارسال‌شده را وارد کنید: ")
    client.login(phone, code)

print("✔ ورود موفق و سشن ذخیره شد.")

# ---------------------------
# AUTO SENDER THREAD
# ---------------------------
def auto_sender():
    while True:
        if config["message"] and config["interval"] > 0:
            chats = client.get_chats()

            for chat in chats:
                if getattr(chat, "type", "") == "group":
                    try:
                        client.send_message(chat.id, config["message"])
                    except Exception as e:
                        print(f"❌ خطا در ارسال پیام به {chat.id}: {e}")
                    time.sleep(1)

        time.sleep(config["interval"])

threading.Thread(target=auto_sender, daemon=True).start()

# ---------------------------
# COMMAND HANDLER
# ---------------------------
print("ربات سروش فعال شد...")

HELP_TEXT = (
    "📘 لیست دستورات:\n"
    "/setmessage <متن> → تنظیم پیام ارسال خودکار\n"
    "/settime <ثانیه> → تنظیم فاصله زمانی ارسال پیام\n"
    "/help → نمایش همین لیست دستورات\n"
)

while True:
    try:
        updates = client.get_updates()
    except Exception as e:
        print(f"❌ خطا در دریافت آپدیت‌ها: {e}")
        time.sleep(5)
        continue

    for update in updates:
        if not update.message or not getattr(update.message, "text", None):
            continue

        text = update.message.text
        chat_id = update.message.chat_id

        # ---- SET MESSAGE ----
        if text.startswith("/setmessage "):
            msg = text.replace("/setmessage ", "").strip()
            config["message"] = msg
            save_config(config)
            client.send_message(chat_id, "✔ پیام ذخیره شد.")
            continue

        # ---- SET TIME ----
        if text.startswith("/settime "):
            try:
                sec = int(text.replace("/settime ", "").strip())
                config["interval"] = sec
                save_config(config)
                client.send_message(chat_id, f"✔ فاصله ارسال تنظیم شد: {sec} ثانیه")
            except:
                client.send_message(chat_id, "❌ مقدار زمان صحیح نیست.")
            continue

        # ---- HELP ----
        if text == "/help":
            client.send_message(chat_id, HELP_TEXT)
            continue

    time.sleep(1)