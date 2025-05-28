from telegram import Update

def update_identifier(update: Update) -> str:
    if update.message is not None:
            return f'{update.message.chat.title} ({update.message.chat.id}) "{update.message.text}"'
    elif update.callback_query is not None:
        return f"{update.callback_query.message.chat.title} ({update.callback_query.message.chat.id}) '{update.callback_query.data}'"
    else:
        return "Unknown"

up_id = update_identifier
