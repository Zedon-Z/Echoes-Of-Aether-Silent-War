from telegram import Update
from telegram.ext import CallbackContext
from storage import database as db
from engine import tasks, win
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    username = query.from_user.username or query.from_user.full_name or f"user{user_id}"

    if data == "join":
        success = db.add_player(chat_id, user_id, query.from_user.full_name)
        db.set_username(chat_id, user_id, username)

        if success:
            players = db.get_player_list(chat_id)
            player_text = "\n".join(
                f"- @{db.get_username(pid) or f'user{pid}'}"
                for pid in players
            )

            join_msg_id = db.get_game_message(chat_id)
            if join_msg_id:
                markup = InlineKeyboardMarkup([[InlineKeyboardButton("Join", callback_data="join")]])
                try:
                    context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=join_msg_id,
                        text=f"📜 Players Joined:\n{player_text}",
                        reply_markup=markup,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    print(f"[WARN] Could not update player list message: {e}")

            query.answer("You joined the match!")
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
