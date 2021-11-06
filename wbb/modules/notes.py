"""
MIT License

Copyright (c) 2021 TheHamkerCat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from re import findall

from pyrogram import filters

from wbb import SUDOERS, USERBOT_ID, USERBOT_PREFIX, app, app2, eor
from wbb.core.decorators.errors import capture_err
from wbb.core.decorators.permissions import adminsOnly
from wbb.core.keyboard import ikb
from wbb.utils.dbfunctions import (delete_note, get_note, get_note_names,
                                   save_note)
from wbb.utils.functions import extract_text_and_keyb

__MODULE__ = "Notes"
__HELP__ = """➤/notes Group a notes save lai mek te en na.

➤/save [note hming] note save na (sticker leh thuziak pangngai pawh a theih ve ve).

#NOTE_NAME To Get A Note.

➤/delete [note hming] Note save tawh Delete na.

/markdownhelp tih hi thawn tawp la format hman tur i hre thei ang
"""


@app2.on_message(
    filters.command("save", prefixes=USERBOT_PREFIX) & filters.user(SUDOERS)
)
@app.on_message(filters.command("save") & ~filters.edited & ~filters.private)
@adminsOnly("can_change_info")
async def save_notee(_, message):
    if len(message.command) < 2 or not message.reply_to_message:
        await eor(
            message,
            text="**Usage:**\nText emaw sticker emaw /save [note hming] ti in reply rawh.",
        )

    elif (
        not message.reply_to_message.text
        and not message.reply_to_message.sticker
    ):
        await eor(
            message,
            text="__**Text emaw stickers notes a save tur chuan reply a /save tih a command angai.**__",
        )
    else:
        name = message.text.split(None, 1)[1].strip()
        if not name:
            return await eor(message, text="**Usage**\n__/save [note hming]__")
        _type = "text" if message.reply_to_message.text else "sticker"
        note = {
            "type": _type,
            "data": message.reply_to_message.text.markdown
            if _type == "text"
            else message.reply_to_message.sticker.file_id,
        }
        prefix = message.text.split()[0][0]
        chat_id = message.chat.id if prefix != USERBOT_PREFIX else USERBOT_ID
        await save_note(chat_id, name, note)
        await eor(message, text=f"__**{name} hi note ah save ani e.**__")


@app2.on_message(
    filters.command("notes", prefixes=USERBOT_PREFIX) & filters.user(SUDOERS)
)
@app.on_message(filters.command("notes") & ~filters.edited & ~filters.private)
@capture_err
async def get_notes(_, message):
    prefix = message.text.split()[0][0]
    is_ubot = bool(prefix == USERBOT_PREFIX)
    chat_id = USERBOT_ID if is_ubot else message.chat.id

    _notes = await get_note_names(chat_id)

    if not _notes:
        return await eor(message, text="**He group ah hian notes save lai a awm rihlo.**")
    _notes.sort()
    msg = f"List of notes in {'USERBOT' if is_ubot else message.chat.title}\n"
    for note in _notes:
        msg += f"**-** `{note}`\n"
    await eor(message, text=msg)


@app2.on_message(
    filters.command("get", prefixes=USERBOT_PREFIX) & filters.user(SUDOERS)
)
async def get_one_note_userbot(_, message):
    if len(message.text.split()) < 2:
        return await eor(message, text="Invalid arguments")

    name = message.text.split(None, 1)[1]

    _note = await get_note(USERBOT_ID, name)
    if not _note:
        return await eor(message, text="No such note.")

    if _note["type"] == "text":
        data = _note["data"]
        await eor(
            message,
            text=data,
            disable_web_page_preview=True,
        )
    else:
        await message.reply_sticker(_note["data"])


@app.on_message(
    filters.regex(r"^#.+") & filters.text & ~filters.edited & ~filters.private
)
@capture_err
async def get_one_note(_, message):
    name = message.text.replace("#", "", 1)
    if not name:
        return
    _note = await get_note(message.chat.id, name)
    if not _note:
        return
    if _note["type"] == "text":
        data = _note["data"]
        keyb = None
        if findall(r"\[.+\,.+\]", data):
            keyboard = extract_text_and_keyb(ikb, data)
            if keyboard:
                data, keyb = keyboard
        await message.reply_text(
            data,
            reply_markup=keyb,
            disable_web_page_preview=True,
        )
    else:
        await message.reply_sticker(_note["data"])


@app2.on_message(
    filters.command("delete", prefixes=USERBOT_PREFIX) & filters.user(SUDOERS)
)
@app.on_message(filters.command("delete") & ~filters.edited & ~filters.private)
@adminsOnly("can_change_info")
async def del_note(_, message):
    if len(message.command) < 2:
        return await eor(message, text="**Usage**\n__/delete [note hming]__")
    name = message.text.split(None, 1)[1].strip()
    if not name:
        return await eor(message, text="**Usage**\n__/delete [note hming]__")

    prefix = message.text.split()[0][0]
    is_ubot = bool(prefix == USERBOT_PREFIX)
    chat_id = USERBOT_ID if is_ubot else message.chat.id

    deleted = await delete_note(chat_id, name)
    if deleted:
        await eor(message, text=f"**Hlawhtling takin note {name} delete ani.**")
    else:
        await eor(message, text="**notes save lai a awmlo.**")
