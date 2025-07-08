from telegram import Update
from telegram.ext import CallbackContext
from engine import phases
from storage import database as db

def phase(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if not db.is_game_active(chat_id):
        update.message.reply_text("No game is active right now.")
        return

    current_phase = db.get_phase(chat_id)
    
    if current_phase == "day":
        db.set_phase(chat_id, "night")
        story = phases.get_night_story()
        update.message.reply_text(f"🌙 *Night Falls...*\n_{story}_", parse_mode="Markdown")
        # Trigger night logic: powers, task checks, deaths, etc.

    elif current_phase == "night":
        db.set_phase(chat_id, "dawn")
        story = phases.get_dawn_story()
        update.message.reply_text(f"🌅 *Dawn Breaks...*\n_{story}_", parse_mode="Markdown")
        # Reveal deaths, resolve events

    elif current_phase == "dawn":
        db.set_phase(chat_id, "day")
        update.message.reply_text("🌞 *A new day begins. Discussion resumes.*", parse_mode="Markdown")
        # Vote resumes

    else:
        db.set_phase(chat_id, "day")
        update.message.reply_text("🔄 Starting Day Phase...", parse_mode="Markdown")
