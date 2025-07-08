from telegram import Update
from telegram.ext import CallbackContext
from storage import database as db
from engine import tasks, win

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if data == "join":
        success = db.add_player(chat_id, user_id, query.from_user.full_name)
        db.set_username(chat_id, user_id, username)
        if success:
            query.answer("You joined the match!")
            query.edit_message_text("✅ You’ve joined the game.")
        else:
            query.answer("Already in the game.")
    elif data.startswith("vote_"):
        target_id = int(data.split("_")[1])
        db.cast_vote(chat_id, user_id, target_id)
        query.answer("Vote recorded.")
        query.edit_message_text("✅ Vote registered.")
    elif data.startswith("task_complete_"):
        code = data.split("_")[-1]
        result = tasks.submit_task(user_id, code)
        query.answer(result)
    elif data.startswith("task_abandon_"):
        result = tasks.abandon_task(user_id)
        query.answer(result)
    elif data == "check_win":
        winner = win.check_for_winner(chat_id)
        if winner:
            query.edit_message_text(f"🏆 *Game Over! Winner:* {winner}", parse_mode="Markdown")
        else:
            query.answer("No winner yet.")