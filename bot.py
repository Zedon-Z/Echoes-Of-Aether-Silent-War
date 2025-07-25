
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import os
from threading import Thread
from handlers import commands, callbacks, game, dm
from config import TOKEN
from telegram import BotCommand

def set_bot_commands(updater):
    command_list = [
        BotCommand("start", "Start the bot"),
        BotCommand("startgame", "Start a new game"),
        BotCommand("join", "Join the current match"),
        BotCommand("forcestart", "Force the game to begin"),
        BotCommand("vote", "Vote to eliminate a player"),
        BotCommand("getchatid", "Get the current group chat ID"),
        BotCommand("flee", "Leave the game lobby before the game starts"),
        BotCommand("extendtime", "Extend the countdown timer"),
        BotCommand("cancelgame", "Cancel the game before it starts"),
        BotCommand("authorize", "Authorize this group (admin only)"),
        BotCommand("deauthorize", "Deauthorize this group (admin only)")
    ]
    updater.bot.set_my_commands(command_list)

def run_bot():
    try:
        updater = Updater(token=TOKEN, use_context=True)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", commands.start))
        dp.add_handler(CommandHandler("startgame", commands.start_game))
        dp.add_handler(CommandHandler("join", commands.join_game))
        dp.add_handler(CommandHandler("vote", commands.vote))
        dp.add_handler(CommandHandler("phase", game.phase))
        dp.add_handler(CommandHandler("getchatid", commands.get_chat_id))
        dp.add_handler(CommandHandler("authorize", commands.authorize))
        dp.add_handler(CommandHandler("deauthorize", commands.deauthorize))
        dp.add_handler(CommandHandler("flee", commands.flee))
        dp.add_handler(CommandHandler("cancelgame", commands.cancel_game))
        dp.add_handler(CommandHandler("nextphase", commands.next_phase))  #temp
        dp.add_handler(CommandHandler("extendtime", commands.extend_time))
        dp.add_handler(CommandHandler("forcestart", commands.force_start))
        dp.add_handler(MessageHandler(Filters.text & Filters.group, game.handle_group_message))
        dp.add_handler(CallbackQueryHandler(callbacks.handle_callback))
        dp.add_handler(MessageHandler(Filters.private & Filters.text, dm.handle_dm))

        set_bot_commands(updater)

        APP_URL = os.getenv("APP_URL")
        PORT = int(os.getenv("PORT", 8443))

        if APP_URL:
            print(f"📡 Starting with webhook: {APP_URL}")
            updater.start_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                webhook_url=f"{APP_URL}/{TOKEN}"
            )
        else:
            print("🟢 Starting in polling mode (local)")
            updater.start_polling()

        updater.idle()

    except Exception as e:
        print(f"[ERROR] Bot failed to start: {e}")

        
if __name__ == "__main__":
    Thread(target=run_bot).start()
    try:
        import server  # Runs the Flask app to expose port
    except Exception as e:
        print(f"[ERROR] Flask server failed to start: {e}")
