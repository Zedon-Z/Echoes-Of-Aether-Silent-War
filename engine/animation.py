import time

def dark_fantasy_animation(bot, chat_id):
    frames = [
        "🌑 *The sky turns pitch black...*",
        "🩸 *A blood moon rises above the ruins...*",
        "👁️‍🗨️ *Eyes blink from the shadows... watching...*",
        "🕸️ *Whispers coil around your soul...*",
        "🖤 *The forgotten curse stirs once again...*",
        "🩸 *It. Has. Begun.* 🩸"
    ]

    msg = bot.send_message(chat_id=chat_id, text=frames[0], parse_mode="Markdown")

    for frame in frames[1:]:
        time.sleep(1.5)
        try:
            bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=frame, parse_mode="Markdown")
        except Exception as e:
            print(f"[WARN] Animation edit failed: {e}")
