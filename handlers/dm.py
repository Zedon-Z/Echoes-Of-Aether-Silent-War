from telegram import Update
from telegram.ext import CallbackContext
from storage import database as db
from engine.roles import use_power
from engine.inventory import use_item

def handle_dm(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.effective_user.id

    def safe_reply(text):
        if update.message:
            update.message.reply_text(text)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    if text.startswith("/usepower"):
        parts = text.split()
        if len(parts) < 2:
            safe_reply("Usage: /usepower @username")
        else:
            result = use_power(user_id, parts[1])
            safe_reply(result)

    elif text.startswith("/useitem"):
        parts = text.split()
        if len(parts) < 2:
            safe_reply("Usage: /useitem item_name")
        else:
            result = use_item(user_id, parts[1])
            safe_reply(result)

    elif text == "/mytasks":
        task = db.get_current_task(user_id)
        if task:
            desc = task.get("desc") or task.get("description") or str(task)
            safe_reply(f"🧾 Your task: {desc}")
        else:
            safe_reply("You have no active task.")

    elif text.startswith("/complete_task"):
        parts = text.split()
        if len(parts) < 2:
            safe_reply("Usage: /complete_task CODE")
        else:
            result = db.complete_task(user_id, parts[1])
            safe_reply(result)

    elif text == "/abandon_task":
        result = db.abandon_current_task(user_id)
        safe_reply(result)

    elif text.startswith("/ally"):
        parts = text.split()
        if len(parts) < 2:
            safe_reply("Usage: /ally @username")
        else:
            target_username = parts[1].replace("@", "")
            target_id = db.get_user_id_by_name(target_username)
            if not target_id:
                safe_reply("User not found.")
            else:
                context.bot.send_message(
                    chat_id=target_id,
                    text=f"{update.effective_user.username} has proposed a secret alliance! Reply with /accept @{update.effective_user.username} to accept.",
                )
                safe_reply("Alliance request sent privately.")

    elif text.startswith("/accept"):
        parts = text.split()
        if len(parts) < 2:
            safe_reply("Usage: /accept @username")
        else:
            target_username = parts[1].replace("@", "")
            target_id = db.get_user_id_by_name(target_username)
            if not target_id:
                safe_reply("User not found.")
            else:
                db.add_alliance(update.effective_chat.id, update.effective_user.id, target_id)
                safe_reply("Alliance formed.")
                try:
                    context.bot.send_message(
                        chat_id=target_id,
                        text=f"{update.effective_user.username} accepted your alliance. You are now linked.",
                    )
                except:
                    pass

    elif text == "/myallies":
        chat_id = update.effective_chat.id
        allies = db.get_allies(chat_id, update.effective_user.id)
        if not allies:
            safe_reply("You have no allies yet.")
        else:
            names = [db.get_username(uid) for uid in allies]
            safe_reply("Your Allies:\n" + "\n".join(f"- {name}" for name in names))

    elif text.startswith("/offer"):
        parts = text.split()
        if len(parts) < 3:
            safe_reply("Usage: /offer @username item_name")
        else:
            target_username = parts[1].replace("@", "")
            item_name = parts[2]
            target_id = db.get_user_id_by_name(target_username)
            if not target_id:
                safe_reply("Target not found.")
            elif item_name not in db.get_inventory(user_id):
                safe_reply("You don't have that item.")
            else:
                if db.offer_item(update.effective_chat.id, user_id, target_id, item_name):
                    safe_reply("Offer sent.")
                    context.bot.send_message(
                        chat_id=target_id,
                        text=f"{update.effective_user.username} offered you '{item_name}'. Use /accept_trade @{update.effective_user.username} to accept."
                    )
                else:
                    safe_reply("You already have a pending offer with this user.")

    elif text.startswith("/accept_trade"):
        parts = text.split()
        if len(parts) < 2:
            safe_reply("Usage: /accept_trade @username")
        else:
            from_username = parts[1].replace("@", "")
            from_id = db.get_user_id_by_name(from_username)
            if not from_id:
                safe_reply("Offer not found.")
            else:
                item = db.accept_offer(update.effective_chat.id, from_id, user_id)
                if item:
                    safe_reply(f"You received '{item}' from @{from_username}.")
                    context.bot.send_message(
                        chat_id=from_id,
                        text=f"{update.effective_user.username} accepted your trade. '{item}' transferred."
                    )
                else:
                    safe_reply("No valid offer found.")

    else:
        safe_reply(
            "Unknown command. Try:\n"
            "• /mytasks\n"
            "• /complete_task <code>\n"
            "• /abandon_task\n"
            "• /usepower @user\n"
            "• /useitem item_name"
        )
