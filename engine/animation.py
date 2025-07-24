import time
from telegram import Bot
#cancel game
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
#Protected

def lumen_priest_animation(bot: Bot, chat_id, target_username):
    main_text = f"🛐 *A sacred aura shields @{target_username} from incoming harm...*"
    second_lines = [
        "🌙 *The darkness recoils...*",
        "⚡ *A burst of light pushes through the void...*",
        "💫 *Celestial chants echo in the distance...*",
        "🌄 *Hope returns to the hearts of the living...*"
    ]

    # Start with empty message
    msg = bot.send_message(chat_id=chat_id, text=".", parse_mode="Markdown")

    # Animate main line letter by letter
    display_text = ""
    for char in main_text:
        display_text += char
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=display_text,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"[WARN] Main line animation failed: {e}")
        time.sleep(0.04)

    # Animate second line frame by frame
    for line in second_lines:
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"{main_text}\n{line}",
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"[WARN] Secondary animation failed: {e}")
        time.sleep(1.5)
#DeathPrediction

def dagger_prophet_success_animation(bot, chat_id, username):
    frames = [
        "🔮 *The dagger trembles...*",
        "🩸 *The cursed name burns bright...*",
        f"💀 *The prophecy unfolds — the blade claims @{username}!*"
    ]

    try:
        msg = bot.send_message(chat_id, text=frames[0], parse_mode="Markdown")
        message_id = msg.message_id
        for frame in frames[1:]:
            time.sleep(1.5)
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=frame, parse_mode="Markdown")
    except Exception as e:
        print(f"[WARN] Dagger Prophet success animation failed: {e}")

def dagger_prophet_fail_message(bot, chat_id):
    try:
        bot.send_message(
            chat_id,
            "❌ *Death Prediction Failed!* Try again after drinking 🐐 *Goat Milk of Foresight*...",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"[WARN] Failed to send dagger fail message: {e}")
