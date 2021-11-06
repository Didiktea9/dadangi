# New file

from pyrogram.filters import command, edited
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from wbb import BOT_USERNAME, app

MARKDOWN = """
Read the below text carefully to find out how formatting works!

<u>Supported Fillings:</u>

<code>{name}</code> - Hei hian user hming kha a mention ang.
<code>{chat}</code> - Heihi chuan Group hming automatic in a hnawhkhat ang.

NOTE: Fillings hi chu greetings module ah chiah awmzia a nei.


<u>Supported formatting:</u>

<code>**Bold**</code> : <b>bold</b> a thuziah na.
<code>~~strike~~</code>: <strike>striked</strike> a thuziah na.
<code>__italic__</code>: <i>italic</i> italic a thuziah na.
<code>--underline--</code>: <u>underline</u> underline a thuziah na.
<code>`code words`</code>: <code>code words</code> siam na.
<code>[hyperlink](google.com)</code>: hetiang <a href='https://www.google.com'>hyperlink</a> link awm a thuziah na.
<b>Note:</b> Markdown & html tags te i hmang thei ve ve.


<u>Button formatting:</u>

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
