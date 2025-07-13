
from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext
from storage import authorized
from telegram.ext import CallbackContext
from telegram import Bot

def schedule_begin_game(chat_id, bot):
    ctx = CallbackContext.from_bot(bot)
    import engine.phases as phases
    phases.begin_game(ctx, chat_id)
    
def create_context(bot: Bot) -> CallbackContext:
    class DummyUpdate:
        effective_chat = None
        effective_user = None

    context = CallbackContext.from_bot(bot)
    context._update = DummyUpdate()
    return context
    
def group_allowed(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        chat_id = update.effective_chat.id
        if not authorized.is_group_authorized(chat_id):
            update.effective_message.reply_text("🔒 This group is not authorized to use the bot.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped
