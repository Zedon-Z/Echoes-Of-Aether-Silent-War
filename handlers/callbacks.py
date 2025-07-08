from telegram import Update
from telegram.ext import CallbackContext
from storage import database as db

def join_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    username = query.from_user.username or f"user{user_id}"

    if db.has_game_started(chat_id):
        query.answer("Game already started!", show_alert=True)
        return

    db.join_game(chat_id, user_id)
    db.set_username(chat_id, user_id, username)

    players = db.get_player_list(chat_id)
    message = "📜 Players Joined:\n"
    for pid in players:
        name = db.get_username(pid) or f"user{pid}"
        message += f"- @{name}\n"

    query.edit_message_text(text=message)