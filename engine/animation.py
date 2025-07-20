import asyncio
from telegram import Bot
from telegram.ext import Application, CommandHandler

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

async def dark_fantasy_animation(bot: Bot, chat_id):
    frames = [
        "🌑 *The sky turns pitch black...*",
        "🩸 *A blood moon rises above the ruins...*",
        "👁️‍🗨️ *Eyes blink from the shadows... watching...*",
        "🕸️ *Whispers coil around your soul...*",
        "🖤 *The forgotten curse stirs once again...*",
        "🩸 *It. Has. Begun.* 🩸"
    ]

    msg = await bot.send_message(chat_id=chat_id, text=frames[0], parse_mode="Markdown")
    
    for frame in frames[1:]:
        await asyncio.sleep(1.5)
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=frame, parse_mode="Markdown")
        except Exception as e:
            print(f"[WARN] Animation edit failed: {e}")

async def start_animation(update, context):
    await dark_fantasy_animation(context.bot, update.effective_chat.id)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start_animation", start_animation))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
