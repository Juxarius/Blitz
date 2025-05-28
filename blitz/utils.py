from telegram import Update

def update_identifier(update: Update) -> str:
    if update.message is not None:
            return f"{update.message.chat.full_name} ({update.message.chat.id})"
    elif update.callback_query is not None:
        return f"{update.callback_query.message.chat.full_name} ({update.callback_query.message.chat.id})"
    else:
        return "Unknown"

up_id = update_identifier
