# New file

from pyrogram.filters import command, edited
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from wbb import BOT_USERNAME, app

MARKDOWN = """
Format diktak a i hman theih nan a hnuai ami te khu chiang takin chhiar ang che!

<u>Fillings hman theih te:</u>

<code>{name}</code> - he format hi chuan user hming mention pahin alo tilang ang.
<code>{chat}</code> - he format hi chu Group hming tihlan na ani ve thung.

NOTE: Greetings module a fillings hman theih te.


<u>Format hman tur te:</u>

<code>**Bold**</code> : Sawtiang saw <b>Hawrawppui</b> a thu ziahna.
<code>~~strike~~</code>: Sawtiang saw <strike>Thaichhiat</strike> na ani.
<code>__italic__</code>: Sawtiang saw <i>italic</i> a ziahna.
<code>--underline--</code>: Sawtiang saw <u>underline</u> a thuziah na.
<code>`code words`</code>: sawtiang saw thuziak <code>code</code> a ziahna.
<code>||spoiler||</code>: Sawtiang saw <spoiler>Spoiler</spoiler> a thu ziahna.
<code>[hyperlink](google.com)</code>: Sawtiang saw thuziak <a href='https://www.google.com'>hyperlink</a> te link a dahna.
<b>Note:</b> Markdown & html tag te i hmang thei ve ve.


<u>Button format ve thung:</u>

-> text ~ [button text, button link]


<u>Example:</u>

<b>example</b> <i>button with markdown</i> <code>formatting</code> ~ [button text, https://google.com]
"""


@app.on_message(command("markdownhelp") & ~edited)
async def mkdwnhelp(_, m: Message):
    keyb = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Min hmet rawh!",
                    url=f"http://t.me/{BOT_USERNAME}?start=mkdwn_help",
                )
            ]
        ]
    )
    if m.chat.type != "private":
        await m.reply(
            "A hnuai a button khu hmet rawh!",
            reply_markup=keyb,
        )
    else:
        await m.reply(
            MARKDOWN, parse_mode="html", disable_web_page_preview=True
        )
    return
