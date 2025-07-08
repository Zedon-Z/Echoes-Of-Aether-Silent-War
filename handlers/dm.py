
from telegram import Update
from telegram.ext import CallbackContext
from storage import database as db
from engine import roles, tasks, inventory

def handle_dm(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Command to list tasks
    if text == "/mytasks":
        task_list = tasks.get_user_tasks(user_id)
        update.message.reply_text(task_list)

    elif text.startswith("/complete_task"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            update.message.reply_text("⚠️ Usage: /complete_task taskcode")
        else:
            code = parts[1]
            result = tasks.submit_task(user_id, code)
            update.message.reply_text(result)

    elif text == "/abandon_task":
        result = tasks.abandon_task(user_id)
        update.message.reply_text(result)

    elif text.startswith("/usepower"):
        parts = text.split()
        if len(parts) < 2:
            update.message.reply_text("Usage: /usepower @username")
            return
        target_username = parts[1]
        result = roles.use_power(user_id, target_username)
        update.message.reply_text(result)

    elif text.startswith("/useitem"):
        parts = text.split()
        if len(parts) < 2:
            update.message.reply_text("Usage: /useitem item_name")
            return
        item = parts[1]
        result = inventory.use_item(user_id, item)
        update.message.reply_text(result)

    else:
        update.message.reply_text(
            "🤖 Unknown command.
"
            "Try:
"
            "• /mytasks
"
            "• /complete_task <code>
"
            "• /abandon_task
"
            "• /usepower @user
"
            "• /useitem item_name"
        )


# --- Alliance Feature Commands ---
elif text.startswith("/ally"):
        parts = text.split()
        if len(parts) < 2:
            update.message.reply_text("Usage: /ally @username")
        else:
            target_username = parts[1].replace("@", "")
            target_id = db.get_user_id_by_name(target_username)
            if not target_id:
                update.message.reply_text("❌ User not found.")
            else:
                context.bot.send_message(
                    chat_id=target_id,
                    text=f"🤝 @{update.effective_user.username} has proposed a secret alliance!\nReply with /accept @{update.effective_user.username} to accept.",
                )
                update.message.reply_text("📨 Your alliance request has been sent privately.")

    elif text.startswith("/accept"):
        parts = text.split()
        if len(parts) < 2:
            update.message.reply_text("Usage: /accept @username")
        else:
            target_username = parts[1].replace("@", "")
            target_id = db.get_user_id_by_name(target_username)
            if not target_id:
                update.message.reply_text("❌ User not found.")
            else:
                db.add_alliance(update.effective_chat.id, update.effective_user.id, target_id)
                update.message.reply_text("✅ Alliance formed.")
                try:
                    context.bot.send_message(
                        chat_id=target_id,
                        text=f"🤝 @{update.effective_user.username} has accepted your alliance. You are now linked.",
                    )
                except:
                    pass

    elif text == "/myallies":
        chat_id = update.effective_chat.id
        allies = db.get_allies(chat_id, update.effective_user.id)
        if not allies:
            update.message.reply_text("🤐 You have no allies yet.")
        else:
            names = [db.get_username(uid) for uid in allies]
            update.message.reply_text("🧩 Your Allies:\n" + "\n".join(f"• {name}" for name in names))

# --- Trade Feature Commands ---
elif text.startswith("/offer"):
        parts = text.split()
        if len(parts) < 3:
            update.message.reply_text("Usage: /offer @username item_name")
        else:
            target_username = parts[1].replace("@", "")
            item_name = parts[2]
            target_id = db.get_user_id_by_name(target_username)
            if not target_id:
                update.message.reply_text("❌ Target not found.")
            elif item_name not in db.get_inventory(user_id):
                update.message.reply_text("❌ You don't have that item.")
            else:
                if db.offer_item(update.effective_chat.id, user_id, target_id, item_name):
                    update.message.reply_text("📤 Offer sent.")
                    context.bot.send_message(
                        chat_id=target_id,
                        text=f"📦 @{update.effective_user.username} has offered you '{item_name}'. Use /accept_trade @{update.effective_user.username} to accept."
                    )
                else:
                    update.message.reply_text("⚠️ You already have a pending offer with this user.")

    elif text.startswith("/accept_trade"):
        parts = text.split()
        if len(parts) < 2:
            update.message.reply_text("Usage: /accept_trade @username")
        else:
            from_username = parts[1].replace("@", "")
            from_id = db.get_user_id_by_name(from_username)
            if not from_id:
                update.message.reply_text("❌ Offer not found.")
            else:
                item = db.accept_offer(update.effective_chat.id, from_id, user_id)
                if item:
                    update.message.reply_text(f"✅ You received '{item}' from @{from_username}.")
                    context.bot.send_message(
                        chat_id=from_id,
                        text=f"🤝 @{update.effective_user.username} accepted your trade. '{item}' has been transferred."
                    )
                else:
                    update.message.reply_text("❌ No valid offer found.")