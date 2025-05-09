from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, PollAnswerHandler, CallbackQueryHandler, CallbackContext, filters
from telegram.ext._contexttypes import ContextTypes
from fastapi import Request, Response
import json

from .utils import debug, info, warning, error
from .utils import up_id
from .utils import get_config
from . import controllers
from . import nlp

endpoint = get_config('endpoint')
webhook_url = f'https://{get_config("ip")}{endpoint}'
bot = controllers.app

async def command_start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    start_msg_lines = [
        'Hello! My name is Blitz~',
        'Im a bill split bot who can help you to log all your expenses for a trip',
        'and make it easy to settle at the end of the trip',
        '',
        'You can type /help to see my commands!',
        '',
        'Recently, I have been trying to pick up human speech as well so you can try to invoke my functionalities '
        'with a \'Hey Blitz\' and simple sentences.',
        'Kinda like \'Hey Siri\', if you dont call my name, I cant reply you.',
        '(づ ◕‿◕ )づ Do be patient with me if I dont understand you.',
        'You can always fall back on my commands~',
        '',
        'I gotta be an admin to hear non-command messages though, so remember to promote me!',
    ]
    info(up_id(update), command='start')
    await update.message.chat.send_message('\n'.join(start_msg_lines))

async def command_help(update: Update, context: CallbackContext):
    help_lines = [
        'For commands, you will need to follow the syntax strictly for it to work',
        '/trip TRIP_NAME - Start a new trip!',
        '/alltrips - Shows you all the trips that you have logged with me!',
        '/bill AMOUNT DESC - Record a receipt that you paid for, I will later ask who you paid for',
        '/settle - Get the final amout everyone owes each other',
        '/receipts - Shows all receipts and breakdown',
        '/show - Shows the currnet trip you are on, you can reselect older trips',
        '/intro - Tell you more about myself!',
        '/divide RATE - Divide all expenses in this trip by a certain amount, for currency conversion',
        '/multiply RATE - Multiple all expenses in this trip by a certain amount, for currency conversion',
    ]
    info(up_id(update), command='help')
    await update.message.chat.send_message('\n'.join(help_lines))

async def command_intro(update: Update, context: CallbackContext):
    introduction = [
        "Hi there! I'm Blitz, your friendly helper bot, always eager to lend a hand!",
        "I'm pretty good at math and keeping track of receipts, especially for end-of-vacation tabulations.",
        "If you've got expenses to split, I've got you covered!",
        "In my spare time, I love chasing down bugs, it's my idea of fun!",
        "I used to live in a cozy Raspberry Pi, thanks to my creator, Juxarius.",
        '\n(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧',
        '\nIt had been there for a while but Jux couldnt get the fan to work, so he had to shut it down before it became a fire hazard.',
        'But then he found out that the connector pins were just wrongly inserted!\nSilly Jux ꒰(･‿･)꒱',
        '',
        'However, it didnt take long before my house got overloaded or something and I was dead for a while.',
        'Nevertheless, Jux kept searching for a new home for me and now I live in the AWS cloud',
        "\nAnyways, feel free to reach out whenever you need some help. I'm here for you!",
    ]
    info(up_id(update), command='intro')
    await update.message.chat.send_message(' '.join(introduction))

async def command_trip(update: Update, context: CallbackContext):
    split_msg = update.message.text.split()
    if len(split_msg) < 2:
        info(f"{up_id(update)} Missing trip name", command='trip', payload=update.message.text)
        await update.message.reply_text(f'Did you miss out the name of your trip?\n/trip TRIP_NAME')
        return
    context.user_data['trip_name'] = ' '.join(split_msg[1:])
    info(up_id(update), command='trip')
    await controllers.new_trip(update, context)

async def command_bill(update: Update, context: CallbackContext):
    split_msg = update.message.text.split()
    if len(split_msg) < 3:
        info(f"{up_id(update)} Missing amount or description", command='bill', payload=update.message.text)
        await update.message.reply_text(f'You gotta put it in this format:\n/bill AMOUNT DESC')
        return
    try:
        amount_str = split_msg[1]
        context.user_data['amount'] = float(amount_str)
    except ValueError as e:
        info(f"{up_id(update)} Invalid amount", command='bill', payload=update.message.text)
        await update.message.reply_text(f'I cant translate {amount_str} to a number!')
        return
    context.user_data.update({
        'amount': amount_str,
        'description': ''.join(split_msg[2:]),
    })
    info(up_id(update), command='bill')
    await controllers.new_receipt(update, context)

async def command_divide(update: Update, context: CallbackContext):
    split_msg = update.message.text.split()
    if len(split_msg) < 2:
        info(f"{up_id(update)} Missing rate", command='divide', payload=update.message.text)
        await update.message.reply_text(f'You need to put the factor to divide by, in this format:\n/divide RATE')
        return
    try:
        context.user_data['rate'] = 1 / float(split_msg[1])
    except ValueError as e:
        info(f"{up_id(update)} Rate not a number", command='divide', payload=update.message.text)
        await update.message.reply_text(f'I cant translate {split_msg[1]} to a number!')
        return
    info(up_id(update), command='divide')
    await controllers.multiply(update, context)

async def command_multiply(update: Update, context: CallbackContext):
    split_msg = update.message.text.split()
    if len(split_msg) < 2:
        info(f"{up_id(update)} Missing rate", command='multiply', payload=update.message.text)
        await update.message.reply_text(f'You need to put the factor to multiply by, in this format:\n/multiply RATE')
        return
    try:
        context.user_data['rate'] = float(split_msg[1])
    except ValueError as e:
        info(f"{up_id(update)} Rate not a number", command='multiply', payload=update.message.text)
        await update.message.reply_text(f'I cant translate {split_msg[1]} to a number!')
        return
    info(up_id(update), command='multiply')
    await controllers.multiply(update, context)

async def poll_complete_bill(update: Update, context: CallbackContext):
    info(up_id(update), command='poll-complete-bill')
    await controllers.complete_receipt(update, context)

async def command_settle(update: Update, context: CallbackContext):
    info(up_id(update), command='settle')
    await controllers.settle(update, context)

async def command_show_receipts(update: Update, context: CallbackContext):
    info(up_id(update), command='show-receipts')
    await controllers.show_receipts(update, context)

async def command_show_trip(update: Update, context: CallbackContext):
    info(up_id(update), command='show-trip')
    await controllers.show_trip(update, context)

async def command_explain(update: Update, context: CallbackContext):
    info(up_id(update), command='explain')
    await controllers.explain(update, context)

async def command_all_my_trips(update: Update, context: CallbackContext):
    info(up_id(update), command='all-my-trips')
    await controllers.all_my_trips(update, context)

async def callback_trip_join(update: Update, context: CallbackContext):
    info(up_id(update), command='callback-trip-join')
    await controllers.join_trip(update, context)

async def callback_trip_browse(update: Update, context: CallbackContext):
    info(up_id(update), command='callback-trip-browse')
    await controllers.change_trip(update, context)

command_map = {
    'start': command_start,
    'intro': command_intro,
    'trip': command_trip,
    'bill': command_bill,
    'settle': command_settle,
    'explain': command_explain,
    'show': command_show_trip,
    'receipts': command_show_receipts,
    'alltrips': command_all_my_trips,
    'help': command_help,
    'divide': command_divide,
    'multiply': command_multiply,
}

callback_map = {
    'trip_join.*': callback_trip_join,
    'trip_browse.*': callback_trip_browse,
}

async def handle_text(update: Update, context: CallbackContext):
    msg = update.message.text
    if not nlp.is_calling_blitz(msg):
        return
    command = nlp.determine_command(msg)
    if command is None:
        info(f"{up_id(update)} Failed to determine command", payload=update.message.text)
        await update.message.reply_text(f'Sorry, I uhh... dont quite understand you ٭(•﹏•)٭')
        return
    parsing_required = {
        'trip': (nlp.parse_trip, controllers.new_trip),
        'bill': (nlp.parse_bill, controllers.new_receipt),
    }
    if command not in parsing_required:
        debug(f"{up_id(update)} No parsing required", command=command, payload=update.message.text)
        await command_map[command](update, context)
        return
    try:
        parsing_required[command][0](msg, context)
        debug(f"{up_id(update)} Parsing succeeded", command=command, payload=update.message.text)
        await parsing_required[command][1](update, context)
    except ValueError as e:
        info(f"{up_id(update)} Parsing failed", command=command, payload=update.message.text)
        await update.message.reply_text(str(e))

async def setup():
    for command, func in command_map.items():
        bot.add_handler(CommandHandler(command, func))

    for callback_pattern, func in callback_map.items():
        bot.add_handler(CallbackQueryHandler(func, callback_pattern))

    poll_handlers = [
        poll_complete_bill,
    ]
    for func in poll_handlers:
        bot.add_handler(PollAnswerHandler(func))

    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    # Do not submit certificate if you are using https already
    await bot.bot.setWebhook(webhook_url)

async def process_request(request: Request):
    req = await request.json()
    debug(json.dumps(req))
    update = Update.de_json(req, bot.bot)
    await bot.process_update(update)
    return Response(status_code=200)
