import os
import re
import time
import json
import random
import requests
from datetime import datetime, timedelta
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# === KONFIGURASI ===
BOT_TOKEN = "8489649514:AAGboIiburC9PSB389XqMJBNRYVnUbSmNiE"
OWNER_ID = 8210180704  # Ganti dengan user ID Telegram kamu (cek @userinfobot)

# Data pengguna (simpan di memori; untuk produksi, gunakan database)
user_db = {}
premium_users = set()
owner_list = {OWNER_ID}

# Path data
DATA_FILE = "user_data.json"

# Banner JPG keren (host di imgur atau github)
BANNER_URL = "https://i.imgur.com/7mW5VQl.jpg"  # Ganti dengan URL gambar JPG-mu

# Muat data lama
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        loaded = json.load(f)
        user_db.update({int(k): v for k, v in loaded.items()})
        premium_users = set(loaded.get("_premium", []))
else:
    user_db = {}

def save_data():
    data = user_db.copy()
    data["_premium"] = list(premium_users)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# === FUNGSI BANTUAN ===
def is_owner(user_id):
    return user_id in owner_list

def is_premium(user_id):
    return user_id in premium_users or is_owner(user_id)

def get_name(user_id):
    return user_db.get(user_id, {}).get("name", "Anonymous")

def add_xp(user_id, xp=10):
    if user_id not in user_db:
        user_db[user_id] = {"xp": 0, "name": "Anonymous", "last_attack": 0, "last_claim": 0}
    user_db[user_id]["xp"] += xp
    save_data()

def level_from_xp(xp):
    return xp // 100 + 1

# === COMMAND HANDLER ===
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = (
        f"🛡️ Selamat datang, <b>{user.first_name}</b>!\n\n"
        f"📸 <a href='{BANNER_URL}'>LIHAT BANNER KEREN</a>\n\n"
        "🛠️ Perintah:\n"
        "/attack <target> - Simulasi serangan\n"
        "/setname <nama> - Ganti nama hacker\n"
        "/profile - Lihat profil\n"
        "/daily - Klaim hadiah harian\n"
        "/tips - Tips keamanan siber\n"
        "/myip - Cek IP publik\n\n"
        "<b>Fitur Premium:</b>\n"
        "/yt <url> - Download YouTube\n"
        "/tt <url> - Download TikTok\n"
        "/ig <url> - Download Instagram\n\n"
        "ℹ️ Bot ini 100% simulasi. Tidak ada serangan nyata!"
    )
    update.message.reply_photo(
        photo=BANNER_URL,
        caption=msg,
        parse_mode=ParseMode.HTML
    )

def attack(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    now = time.time()
    last = user_db.get(user_id, {}).get("last_attack", 0)
    if now - last < 60:
        return update.message.reply_text("⏳ Tunggu 60 detik sebelum menyerang lagi!")
    
    if not context.args:
        return update.message.reply_text("UsageId: /attack <target>")
    
    target = context.args[0]
    if any(word in target.lower() for word in ["gov", "admin", "bank", "localhost", "192.168"]):
        return update.message.reply_text("❌ Target tidak diizinkan!")

    chat_id = update.effective_chat.id
    name = get_name(user_id)
    msg = context.bot.send_message(chat_id, f"📡 <b>{name}</b> memulai serangan ke <code>{target}</code>...", parse_mode=ParseMode.HTML)

    for i in range(1, 6):
        time.sleep(1)
        bar = "█" * i + "░" * (5 - i)
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,
            text=f"📡 Menyerang <code>{target}</code>...\n[{bar}] {i*20}%",
            parse_mode=ParseMode.HTML
        )
    
    add_xp(user_id, 20)
    user_db[user_id]["last_attack"] = now
    save_data()
    
    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg.message_id,
        text=f"✅ Serangan selesai!\nTarget: <code>{target}</code>\nStatus: Masih hidup 😅\n\n"
             f"💡 Tips: Jangan lakukan DDoS – ilegal dan merugikan!",
        parse_mode=ParseMode.HTML
    )

def setname(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not context.args:
        return update.message.reply_text("UsageId: /setname <nama>")
    name = " ".join(context.args)[:20]
    if user_id not in user_db:
        user_db[user_id] = {"xp": 0, "name": name, "last_attack": 0, "last_claim": 0}
    else:
        user_db[user_id]["name"] = name
    save_data()
    update.message.reply_text(f"✅ Nama hacker kamu sekarang: <b>{name}</b>", parse_mode=ParseMode.HTML)

def profile(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in user_db:
        return update.message.reply_text("Kirim /attack dulu untuk membuat profil!")
    name = get_name(user_id)
    xp = user_db[user_id]["xp"]
    level = level_from_xp(xp)
    badge = "🥉 Script Kiddie" if level < 5 else "🥈 Phantom Hacker" if level < 10 else "🥇 Digital Ghost"
    update.message.reply_text(
        f"👤 <b>{name}</b>\n"
        f"📊 XP: {xp}\n"
        f"🏅 Level: {level}\n"
        f"🎖️ Badge: {badge}\n"
        f"🌟 Status: {'👑 OWNER' if is_owner(user_id) else '💎 PREMIUM' if is_premium(user_id) else '👤 USER'}",
        parse_mode=ParseMode.HTML
    )

def daily(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    now = datetime.now()
    last = user_db.get(user_id, {}).get("last_claim", 0)
    last_dt = datetime.fromtimestamp(last) if last else None
    if last_dt and (now - last_dt).days < 1:
        return update.message.reply_text("📆 Hadiah harian sudah diklaim! Coba lagi besok.")
    add_xp(user_id, 50)
    user_db[user_id]["last_claim"] = time.time()
    save_data()
    update.message.reply_text("🎁 Kamu mendapat 50 XP! Klaim lagi besok ya~")

def tips(update: Update, context: CallbackContext):
    tips_list = [
        "🔐 Gunakan password kuat & unik untuk setiap akun.",
        "🔄 Update software secara rutin untuk hindari celah keamanan.",
        "📧 Jangan klik link mencurigakan di email atau pesan.",
        "2FA > Password. Selalu aktifkan verifikasi dua langkah!",
        "💾 Backup data penting secara berkala."
    ]
    update.message.reply_text("💡 Tips Keamanan Siber:\n\n" + random.choice(tips_list))

def myip(update: Update, context: CallbackContext):
    try:
        ip = requests.get("https://api.ipify.org", timeout=5).text
        update.message.reply_text(f"🌐 IP Publik Kamu: <code>{ip}</code>", parse_mode=ParseMode.HTML)
    except:
        update.message.reply_text("❌ Gagal mendapatkan IP.")

# === SISTEM OWNER & PREMIUM ===
def addowner(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return update.message.reply_text("❌ Hanya owner utama yang bisa menambah owner.")
    if not context.args:
        return update.message.reply_text("UsageId: /addowner <user_id>")
    try:
        uid = int(context.args[0])
        owner_list.add(uid)
        update.message.reply_text(f"✅ User {uid} ditambahkan sebagai owner!")
    except:
        update.message.reply_text("❌ ID harus berupa angka!")

def addpremium(update: Update, context: CallbackContext):
    if not is_owner(update.effective_user.id):
        return update.message.reply_text("❌ Hanya owner yang bisa menambah premium.")
    if not context.args:
        return update.message.reply_text("UsageId: /addpremium <user_id>")
    try:
        uid = int(context.args[0])
        premium_users.add(uid)
        save_data()
        update.message.reply_text(f"✅ User {uid} sekarang PREMIUM! 🌟")
    except:
        update.message.reply_text("❌ ID harus berupa angka!")

# === DOWNLOAD MEDIA (PREMIUM ONLY) ===
def download_yt(update: Update, context: CallbackContext):
    if not is_premium(update.effective_user.id):
        return update.message.reply_text("💎 Fitur ini hanya untuk user PREMIUM! Hubungi owner.")
    if not context.args:
        return update.message.reply_text("UsageId: /yt <url_youtube>")
    url = context.args[0]
    if "youtube.com" not in url and "youtu.be" not in url:
        return update.message.reply_text("❌ URL YouTube tidak valid!")
    try:
        update.message.reply_text("🎥 Sedang memproses video YouTube...")
        os.system(f"yt-dlp -f 'best[height<=480]' -o 'video.mp4' '{url}'")
        if os.path.exists("video.mp4"):
            with open("video.mp4", "rb") as f:
                update.message.reply_video(f, caption="✅ Video berhasil diunduh!")
            os.remove("video.mp4")
        else:
            update.message.reply_text("❌ Gagal mengunduh video.")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def download_tt(update: Update, context: CallbackContext):
    if not is_premium(update.effective_user.id):
        return update.message.reply_text("💎 Fitur ini hanya untuk user PREMIUM!")
    if not context.args:
        return update.message.reply_text("UsageId: /tt <url_tiktok>")
    url = context.args[0]
    try:
        update.message.reply_text("📱 Sedang memproses video TikTok...")
        # Gunakan layanan API publik (contoh sederhana via requests)
        # CATATAN: TikTok sering ubah struktur, jadi ini mungkin perlu update
        # Alternatif: gunakan library seperti `tiktok-scraper` jika tersedia
        r = requests.post("https://tikcdn.io/ss", data={"url": url})
        if r.status_code == 200:
            video_url = r.json().get("video")
            if video_url:
                video = requests.get(video_url)
                with open("tiktok.mp4", "wb") as f:
                    f.write(video.content)
                with open("tiktok.mp4", "rb") as f:
                    update.message.reply_video(f, caption="✅ Video TikTok tanpa watermark!")
                os.remove("tiktok.mp4")
                return
        update.message.reply_text("❌ Gagal mengunduh TikTok.")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def download_ig(update: Update, context: CallbackContext):
    if not is_premium(update.effective_user.id):
        return update.message.reply_text("💎 Fitur ini hanya untuk user PREMIUM!")
    if not context.args:
        return update.message.reply_text("UsageId: /ig <url_instagram>")
    url = context.args[0]
    try:
        update.message.reply_text("📸 Sedang memproses konten Instagram...")
        # Instaloader tidak cocok untuk bot publik, jadi gunakan parsing sederhana
        # Hanya untuk post publik
        shortcode = re.search(r"/(p|reel)/([^/]+)", url)
        if not shortcode:
            return update.message.reply_text("❌ URL Instagram tidak valid!")
        # Di Termux, Instaloader bisa dipakai, tapi butuh login
        # Untuk demo, kita kirim placeholder
        update.message.reply_text("🚧 Fitur Instagram dalam pengembangan! Coba YouTube/TikTok dulu.")
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

# === MAIN ===
def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher

    # Public commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("attack", attack))
    dp.add_handler(CommandHandler("setname", setname))
    dp.add_handler(CommandHandler("profile", profile))
    dp.add_handler(CommandHandler("daily", daily))
    dp.add_handler(CommandHandler("tips", tips))
    dp.add_handler(CommandHandler("myip", myip))

    # Owner commands
    dp.add_handler(CommandHandler("addowner", addowner))
    dp.add_handler(CommandHandler("addpremium", addpremium))

    # Premium commands
    dp.add_handler(CommandHandler("yt", download_yt))
    dp.add_handler(CommandHandler("tt", download_tt))
    dp.add_handler(CommandHandler("ig", download_ig))

    updater.start_polling()
    print("✅ Bot berjalan di Termux!")
    updater.idle()

if __name__ == "__main__":
    main()
