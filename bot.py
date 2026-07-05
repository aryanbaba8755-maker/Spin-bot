# import random
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler

# --- GLOBAL CONFIGURATION & CACHE ---
CURRENT_MODE = 'all'  # Default mode 'all' rahega
VIDEO_CACHE = []      # Super-fast speed ke liye memory cache
OWNER_ID = 2107169286 # Aapki Telegram ID

# Speed Optimization: Files ko startup par hi load karna (Zero Delay System)
def load_video_cache():
    global VIDEO_CACHE
    try:
        all_files = os.listdir('.')
        valid_extensions = ('.mp4', '.gif')
        VIDEO_CACHE = [f for f in all_files if f.lower().endswith(valid_extensions)]
        print(f"Fast Storage Active: {len(VIDEO_CACHE)} files loaded into memory.")
    except Exception as e:
        print(f"Cache load karne me error: {e}")

# --- SECURITY CHECKS ---
# Sirf /spin command ke liye Admin check
async def is_authorized_for_spin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.message.from_user:
        return False
        
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    
    if update.message.chat.type in ['group', 'supergroup']:
        try:
            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            if bot_member.status != 'administrator':
                return False
                
            owner_member = await context.bot.get_chat_member(chat_id, OWNER_ID)
            if owner_member.status not in ['administrator', 'creator']:
                return False

            user_member = await context.bot.get_chat_member(chat_id, user_id)
            is_user_admin = user_member.status in ['administrator', 'creator']
            return is_user_admin or user_id == OWNER_ID
            
        except Exception as e:
            return False
    else:
        return user_id == OWNER_ID

# --- ANTI-ADD SECURITY (Koi aur group me add nahi kar payega) ---
async def track_bot_additions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    # Agar bot ko kisi group me add kiya gaya hai
    if result.new_chat_member.status in ["member", "administrator"]:
        added_by = result.from_user.id
        chat_id = result.chat.id
        
        # Agar add karne wala Owner nahi hai, toh turant leave kardo
        if added_by != OWNER_ID:
            print(f"Unauthorized addition by {added_by}. Bot leaving chat {chat_id}.")
            await context.bot.leave_chat(chat_id)

# Auto-Leave Rule: Agar Owner group chhod deta hai toh Bot bhi chhod dega
async def check_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    left_member = update.message.left_chat_member
    if left_member and left_member.id == OWNER_ID:
        try:
            await context.bot.leave_chat(update.message.chat_id)
            print("Owner left. Bot auto-left successfully.")
        except Exception as e:
            pass

# --- SPECIAL COMMANDS (ONLY FOR OWNER) ---

# [/18] Command: Random Mode
async def set_random_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    # STRICT CHECK: Sirf Owner hi command de sakta hai
    if update.message.from_user.id != OWNER_ID:
        return

    CURRENT_MODE = 'all'  # Global change
    # Sirf command wale group me turant (fast) reply dega
    await update.message.reply_text("✅ Random mode active")

# [/77] Command: Odd Mode
async def set_odd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    # STRICT CHECK: Sirf Owner hi command de sakta hai
    if update.message.from_user.id != OWNER_ID:
        return

    CURRENT_MODE = 'odd'  # Global change
    await update.message.reply_text("✅ Odd mode active")

# [/66] Command: Even Mode
async def set_even_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    # STRICT CHECK: Sirf Owner hi command de sakta hai
    if update.message.from_user.id != OWNER_ID:
        return

    CURRENT_MODE = 'even'  # Global change
    await update.message.reply_text("✅ Even mode active")


# --- FAST SPIN SYSTEM ---
# [/spin] Command: Precise 1:1 Instant Reply System
async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE, VIDEO_CACHE
    if not await is_authorized_for_spin(update, context):
        return

    if not VIDEO_CACHE:
        load_video_cache()

    if not VIDEO_CACHE:
        return

    try:
        final_filtered_list = []

        if CURRENT_MODE == 'odd':
            for f in VIDEO_CACHE:
                name_part = os.path.splitext(f)[0]
                if name_part.isdigit() and int(name_part) % 2 != 0:
                    final_filtered_list.append(f)
                    
        elif CURRENT_MODE == 'even':
            for f in VIDEO_CACHE:
                name_part = os.path.splitext(f)[0]
                if name_part.isdigit() and int(name_part) % 2 == 0:
                    final_filtered_list.append(f)
                    
        else:
            final_filtered_list = VIDEO_CACHE

        # Extremely fast response: file memory se select hokar direct send
        if final_filtered_list:
            selected_file = random.choice(final_filtered_list)
            await update.message.reply_animation(animation=open(selected_file, 'rb'))

    except Exception as e:
        print(f"Spin command error: {e}")

def main():
    # Yahan apna Bot Token daalein
    TOKEN = "8826711613:AAFinY686gPTxoLNef0tXpHEGimPCC5ffRs"

    load_video_cache()

    application = Application.builder().token(TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("spin", spin))
    application.add_handler(CommandHandler("18", set_random_mode))
    application.add_handler(CommandHandler("77", set_odd_mode))
    application.add_handler(CommandHandler("66", set_even_mode))
    
    # Security Handlers
    application.add_handler(ChatMemberHandler(track_bot_additions, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, check_left_member))

    print("Ultra-Fast & Secure Bot is Ready!")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()


Is code me delay ki koi whja dikh rhi hai jisse bot delay kr rha reply dene meSpin-bot
