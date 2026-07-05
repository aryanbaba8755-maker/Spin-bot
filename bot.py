import random
import os
import threading
import sys
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ChatMemberHandler
)

# --- CONFIGURATION ---
OWNER_ID = 2107169286 
TOKEN = "8826711613:AAFsik9dxiFywk_G6As_xxGrUAiKa4MgYTs"
CURRENT_MODE = 'all' 
VIDEO_CACHE = []

# --- FLASK FOR RENDER ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Live and Secure"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# --- CORE LOGIC ---
def load_video_cache():
    global VIDEO_CACHE
    # Sirf digits wali files uthayega (1.mp4, 2.gif etc)
    VIDEO_CACHE = [f for f in os.listdir('.') if f.lower().endswith(('.mp4', '.gif'))]

# Security: Check if User is Admin or Owner
async def is_admin_or_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.message.from_user: return False
    user_id = update.message.from_user.id
    
    if user_id == OWNER_ID: return True
    
    if update.message.chat.type in ['group', 'supergroup']:
        try:
            member = await context.bot.get_chat_member(update.message.chat_id, user_id)
            return member.status in ['administrator', 'creator']
        except: return False
    return False

# Security: Anti-Add (Leave if not added by Owner)
async def track_bot_additions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if result.new_chat_member.status in ["member", "administrator"]:
        if result.from_user.id != OWNER_ID:
            await context.bot.leave_chat(result.chat.id)

# Security: Leave if Owner leaves
async def check_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.left_chat_member and update.message.left_chat_member.id == OWNER_ID:
        await context.bot.leave_chat(update.message.chat_id)

# --- COMMANDS ---
async def set_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    if update.message.from_user.id != OWNER_ID: return 
    
    cmd = update.message.text
    if "/18" in cmd: CURRENT_MODE = 'all'; msg = "✅ Random mode active"
    elif "/77" in cmd: CURRENT_MODE = 'odd'; msg = "✅ Odd mode active"
    elif "/66" in cmd: CURRENT_MODE = 'even'; msg = "✅ Even mode active"
    
    await update.message.reply_text(msg)

async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE, VIDEO_CACHE
    if not await is_admin_or_owner(update, context): return # Silent Ignore
    
    if not VIDEO_CACHE: load_video_cache()
    
    filtered = []
    for f in VIDEO_CACHE:
        name_part = os.path.splitext(f)[0]
        if not name_part.isdigit(): continue
        val = int(name_part)
        
        if CURRENT_MODE == 'odd' and val % 2 != 0: filtered.append(f)
        elif CURRENT_MODE == 'even' and val % 2 == 0: filtered.append(f)
        elif CURRENT_MODE == 'all': filtered.append(f)

    if filtered:
        selected = random.choice(filtered)
        with open(selected, 'rb') as anim:
            await update.message.reply_animation(animation=anim)

def main():
    # Start Flask in background
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Build Bot
    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("spin", spin))
    application.add_handler(CommandHandler(["18", "77", "66"], set_mode))
    application.add_handler(ChatMemberHandler(track_bot_additions, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, check_left_member))

    # Start Polling
    print("Bot is fully armed and running!")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
    
