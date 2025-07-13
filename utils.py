import engine.phases as phases
from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext
from storage import authorized
    
def group_allowed(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        chat_id = update.effective_chat.id
        if not authorized.is_group_authorized(chat_id):
            update.effective_message.reply_text("🔒 This group is not authorized to use the bot.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped
