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
#✅Dayanimation
def send_alive_players_animation(chat_id, bot):
    from storage import database as db
    players = db.get_alive_players(chat_id)
    usernames = [f"@{db.get_username(pid)}" for pid in players]

    if not usernames:
        bot.send_message(chat_id, "⚰️ No one remains in the realm of echoes...")
        return

    title = "🌅 *Dawn Breaks Over Aether...*"
    dramatic_intro = "✨ The following souls still walk among us:"
    msg = bot.send_message(chat_id, text=title, parse_mode="Markdown")

    # Animate the message title
    for dots in ["🌅 *Dawn Breaks.*", "🌅 *Dawn Breaks..*", "🌅 *Dawn Breaks...*"]:
        time.sleep(0.6)
        bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=dots, parse_mode="Markdown")

    time.sleep(0.8)
    bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"{title}\n\n{dramatic_intro}", parse_mode="Markdown")

    # One by one reveal players
    for i, username in enumerate(usernames, 1):
        time.sleep(0.7)
        text = f"{title}\n\n{dramatic_intro}\n" + "\n".join([f"🔹 {u}" for u in usernames[:i]])
        bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=text, parse_mode="Markdown")
#CancelAnimation
def cancel_game_animation(bot, chat_id):
    from time import sleep

    frames = [
        "🌒 *Whispers falter...*",
        "🔮 *The Circle of Fate trembles...*",
        "🩸 *Sigils burn. Candles snuff out.*",
        "🌫️ *Aether unravels... the ritual is broken.*",
        "📜 *All echoes are silenced...*",
        "❌ *The game has been cancelled.*"
    ]

    try:
        msg = bot.send_message(chat_id=chat_id, text=frames[0], parse_mode="Markdown")
        message_id = msg.message_id

        for frame in frames[1:]:
            sleep(1.4)
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=frame, parse_mode="Markdown")

    except Exception as e:
        print(f"[WARN] Cancel animation failed: {e}")
####
def core_reverser_animation(bot, chat_id):
    frames = [
        "🔄 *The Core begins to spin...*",
        "🌀 *Reality twists. Votes scatter across the veil...*",
        "🎲 *Fate has chosen anew.*"
    ]
    msg = bot.send_message(chat_id, text=frames[0], parse_mode="Markdown")
    for frame in frames[1:]:
        time.sleep(1.5)
        bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=frame, parse_mode="Markdown")
