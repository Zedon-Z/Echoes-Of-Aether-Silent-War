from engine.phases import start_day_phase, start_night_phase   #temp
from engine.animation import cancel_game_animation
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from storage import database as db
from engine import phases
from functools import partial
import time

# Track join message ID to update later
join_message_tracker = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Welcome to *Echoes of Aether: The Silent War.*\n\n"
        "Use /startgame to begin a new game, or /join to join one.",
        parse_mode='Markdown'
    )

# ----- START GAME -----
def start_game(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if db.is_game_active(chat_id):
        update.message.reply_text("⚠️ A game is already running!")
        return

    db.start_new_game(chat_id)
    countdown = 60
    db.set_timer(chat_id, countdown)
    db.set_game_start_time(chat_id, int(time.time()) + countdown)

    # Schedule game to begin after countdown
    context.job_queue.run_once(lambda ctx: begin_game(ctx, chat_id), countdown)
    # Schedule countdown alerts with emoji
    def countdown_alert(seconds_left):
      def alert_fn(ctx: CallbackContext):
        emoji = "⏳" if seconds_left > 5 else "🚨"
        ctx.bot.send_message(
            chat_id=chat_id,
            text=f"{emoji} *{seconds_left} seconds left before the game begins!*",
            parse_mode='Markdown'
        )
        return alert_fn

# Schedule alerts only if enough time exists
    if countdown >= 30:
      context.job_queue.run_once(lambda ctx: countdown_alert(30, chat_id)(ctx), countdown - 30)
    if countdown >= 10:
      context.job_queue.run_once(lambda ctx: countdown_alert(10, chat_id)(ctx), countdown - 10)
    if countdown >= 5:
       context.job_queue.run_once(lambda ctx: countdown_alert(5, chat_id)(ctx), countdown - 5)
    # Join button (static message)
    join_btn = [[InlineKeyboardButton("🔹 Join Game", callback_data="join")]]
    context.bot.send_message(
        chat_id=chat_id,
        text="🧩 *Echoes of Aether Begins!*\nClick below to join the match!",
        reply_markup=InlineKeyboardMarkup(join_btn),
        parse_mode='Markdown'
    )

    # Player list message (we will update this on each join)
    player_msg = context.bot.send_message(
        chat_id=chat_id,
        text="📜 *Players Joined:*\n_(Waiting...)_",
        parse_mode='Markdown'
    )

    # Save message_id so /join and inline button can update the same message
    db.set_game_message(chat_id, player_msg.message_id)

# ----- JOIN GAME -----
def join_game(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if not db.is_game_active(chat_id):
        update.message.reply_text("No game has been started yet.")
        return

    username = user.username or user.full_name or f"user{user.id}"
    success = db.add_player(chat_id, user.id, user.full_name)
    db.set_username(chat_id, user.id, username)

    if not success:
        update.message.reply_text("ℹ️ You're already in the game.")
        return

    # Build player list
    players = db.get_player_list(chat_id)
    player_text = "\n".join(f"- @{db.get_username(pid) or f'user{pid}'}" for pid in players)

    join_msg_id = db.get_game_message(chat_id)
    if join_msg_id:
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Join", callback_data="join")]])
        try:
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=join_msg_id,
                text=f"📜 Players Joined:\n{player_text}",
                reply_markup=markup
            )
        except Exception as e:
            print(f"[WARN] Could not update player list message: {e}")

def extend_time(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if not db.is_game_active(chat_id):
        update.message.reply_text("❌ No active game to extend time for.")
        return

    db.extend_timer(chat_id, 30)
    update.message.reply_text("⏳ Extra time added! Waiting for more players...")

def flee(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if not db.is_game_active(chat_id):
        update.message.reply_text("❌ There's no game to flee from.")
        return

    if db.remove_player(chat_id, user.id):
        update.message.reply_text(f"🚪 {user.full_name} has left the game.")
    else:
        update.message.reply_text("You’re not part of the game.")

def vote(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not db.is_game_active(chat_id):
        update.message.reply_text("No game in progress.")
        return

    players = db.get_player_list(chat_id)
    if not players:
        update.message.reply_text("No players found.")
        return

    buttons = [
        [InlineKeyboardButton(name, callback_data=f"vote_{pid}")]
        for pid, name in players.items()
    ]
    update.message.reply_text("🔍 *Vote for a suspect:*", reply_markup=InlineKeyboardMarkup(buttons), parse_mode='Markdown')

def force_start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if db.has_game_started(chat_id):
        update.message.reply_text("⚠️ The game has already started.")
        return
    if not db.is_game_active(chat_id):
        update.message.reply_text("❌ No game to start.")
        return

    players = db.get_player_list(chat_id)
    if len(players) < 3:
        update.message.reply_text("⚠️ At least 3 players are needed to start the game.")
        return

    update.message.reply_text("🚀 Forcing game start...")
    phases.begin_game(context, chat_id)  # ✅ Start full game logic

def get_chat_id(update: Update, context: CallbackContext):
    update.message.reply_text(f"Chat ID: `{update.effective_chat.id}`", parse_mode='Markdown')

from config import BOT_OWNER_ID
from storage import authorized

def authorize(update: Update, context: CallbackContext):
    if update.effective_user.id != BOT_OWNER_ID:
        update.message.reply_text("🚫 You are not authorized to do this.")
        return

    chat_id = update.effective_chat.id
    if authorized.add_group(chat_id):
        update.message.reply_text(f"✅ This group ({chat_id}) is now authorized.")
    else:
        update.message.reply_text("ℹ️ This group is already authorized.")

def deauthorize(update: Update, context: CallbackContext):
    if update.effective_user.id != BOT_OWNER_ID:
        update.message.reply_text("🚫 You are not authorized to do this.")
        return

    chat_id = update.effective_chat.id
    if authorized.remove_group(chat_id):
        update.message.reply_text(f"❌ This group ({chat_id}) has been removed from authorized list.")
    else:
        update.message.reply_text("ℹ️ This group wasn't authorized.")

from engine.animation import dark_fantasy_animation

def cancel_game(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if not db.is_game_active(chat_id):
        update.message.reply_text("❌ There’s no active game to cancel.")
        return

    db.cancel_game(chat_id)

    # Send initial cancellation message
    update.message.reply_text("🚫 *The game has been cancelled.* Watch closely...", parse_mode='Markdown')

    # Trigger dark animation
    try:
        cancel_game_animation(context.bot, chat_id)
    except Exception as e:
        print(f"[WARN] Failed to run animation: {e}")
        
def has_game_started(chat_id):
    return games.get(chat_id, {}).get("started", False)

def mark_game_started(chat_id):
    if chat_id in games:
        games[chat_id]["started"] = True
#Temprory


def next_phase(update, context):
    chat_id = update.effective_chat.id
    current_phase = db.get_phase(chat_id)

    if not db.is_game_active(chat_id):
        update.message.reply_text("⚠️ No active game running.")
        return

    if current_phase == "day":
        start_night_phase(chat_id, context)
        update.message.reply_text("🌙 Transitioned to Night Phase manually.")
    elif current_phase == "night":
        start_day_phase(chat_id, context)
        update.message.reply_text("🌅 Transitioned to Day Phase manually.")
    else:
        update.message.reply_text("⚠️ Unknown phase state.")
