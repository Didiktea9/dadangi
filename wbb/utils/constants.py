# New file

from pyrogram.filters import command, edited
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from wbb import BOT_USERNAME, app

MARKDOWN = """
Format diktak a i hman theih nan a hnuai ami hi ngun takin chhiar rawh!

<u>Supported Fillings:</u>

<code>{name}</code> - Hei hian user hming kha a mention ang.
<code>{chat}</code> - Heihi chuan Group hming automatic in a hnawhkhat ang.

NOTE: Fillings hi chu greetings module ah chiah awmzia a nei.


<u>Format Hman theih te:</u>

<code>**Bold**</code> : Sawtiang sign hmang a i thu kual khung a piang kha <b>bold</b> (hawrawp hraw bik) ah a chang ang.
<code>~~strike~~</code>: Sawtiang sign hmang a i thu kual khung a piang kha <strike>striked</strike> (hawrawp thaichhiat) ah a chang ang.
<code>__italic__</code>: Sawtiang sign hmang a i thu kual khung a piang kha <i>italic</i> italic (thuziak awn) ah a chang ang.
<code>--underline--</code>: Sawtiang sign hmang a i thu kual khung a piang kha <u>underline</u> underline (ahnuai in rin) ah a chang ang.
<code>`code words`</code>: Sawtiang sign hmang a i thu kual khung a piang kha <code>code words</code> hawrawp kar ah a chang ang.
<code>[hyperlink](google.com)</code>: hetiang <a href='https://www.google.com'>hyperlink</a> link awm a thuziah na.
<b>Note:</b> Markdown & html tags te i hmang thei ve ve.


<u>Button Siamdan:</u>

-> text ~ [button text, button link]


<u>Entirna:</u>

<b>entirna</b> <i>markdown hmang a button</i> <code>siam dan</code> ~ [button text, https://google.com]
"""


@app.on_message(command("markdownhelp") & ~edited)
async def mkdwnhelp(_, m: Message):
    keyb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Click Here!",
                    url=f"http://t.me/{BOT_USERNAME}?start=mkdwn_help",
                )
            ]
        ]
    )
    if m.chat.type != "private":
        await m.reply(
            "Click on the below button to get markdown usage syntax in pm!",
            reply_markup=keyb,
        )
    else:
        await m.reply(
            MARKDOWN, parse_mode="html", disable_web_page_preview=True
        )
    return
