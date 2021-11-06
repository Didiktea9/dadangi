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
import asyncio

from pyrogram import filters
from pyrogram.types import Message

from wbb import BOT_ID, SUDOERS, USERBOT_ID, app, app2
from wbb.core.decorators.errors import capture_err

__MODULE__ = "Pipes"
__HELP__ = """
**HE MODULE HI CHU DEVS TAN BIK AW**

He module hi  gruop/channel atang a adang a forward na ani.


➤/activate_pipe [group id] [group dang id] [BOT|USERBOT]

    Active a pipe.

    'BOT' emaw 'USERBOT' emaw zawk zawk i hmang thei a,
    pakhat zawk zawk khian group
    message te a va thur chhuak ang.


➤/deactivate_pipe [FROM_CHAT_ID]
    Pipe deactive na.


➤/show_pipes
    pipes active lai en na.

**NOTE:**
    He Pipes hi chu temporary mai ani a, bot restart in
    set that leh zel angai.
"""
pipes_list_bot = {}
pipes_list_userbot = {}


@app.on_message(~filters.me, group=500)
@capture_err
async def pipes_worker_bot(_, message: Message):
    chat_id = message.chat.id
    if chat_id in pipes_list_bot:
        await message.forward(pipes_list_bot[chat_id])


@app2.on_message(~filters.me, group=500)
@capture_err
async def pipes_worker_userbot(_, message: Message):
    chat_id = message.chat.id

    if chat_id in pipes_list_bot:
        caption = f"\n\nForwarded from `{chat_id}`"
        to_chat_id = pipes_list_bot[chat_id]

        if not message.text:
            m, temp = await asyncio.gather(
                app.listen(USERBOT_ID), message.copy(BOT_ID)
            )
            caption = f"{temp.caption}{caption}" if temp.caption else caption

            await app.copy_message(
                to_chat_id,
                USERBOT_ID,
                m.message_id,
                caption=caption,
            )
            await asyncio.sleep(2)
            return await temp.delete()

        await app.send_message(to_chat_id, text=message.text + caption)


@app.on_message(filters.command("activate_pipe") & filters.user(SUDOERS))
@capture_err
async def activate_pipe_func(_, message: Message):
    global pipes_list_bot, pipes_list_userbot

    if len(message.command) != 4:
        return await message.reply(
            "**Usage:**\n/activate_pipe [Group id] [Group dang id] [BOT|USERBOT]"
        )

    text = message.text.strip().split()

    from_chat = int(text[1])
    to_chat = int(text[2])
    fetcher = text[3].lower()

    if fetcher not in ["bot", "userbot"]:
        return await message.reply("Diklo tlat, tih that leh angai.")

    if from_chat in pipes_list_bot or from_chat in pipes_list_userbot:
        return await message.reply_text("He pipe hi a active mek e.")

    dict_ = pipes_list_bot
    if fetcher == "userbot":
        dict_ = pipes_list_userbot

    dict_[from_chat] = to_chat
    await message.reply_text("Activated pipe.")


@app.on_message(filters.command("deactivate_pipe") & filters.user(SUDOERS))
@capture_err
async def deactivate_pipe_func(_, message: Message):
    global pipes_list_bot, pipes_list_userbot

    if len(message.command) != 2:
        await message.reply_text("**Usage:**\n/deactivate_pipe [FROM_CHAT_ID]")
        return
    text = message.text.strip().split()
    from_chat = int(text[1])

    if from_chat not in pipes_list_bot and from_chat not in pipes_list_userbot:
        await message.reply_text("he pipe hi chu a active tawhlo.")

    dict_ = pipes_list_bot
    if from_chat in pipes_list_userbot:
        dict_ = pipes_list_userbot

    del dict_[from_chat]
    await message.reply_text("Deactivated pipe.")


@app.on_message(filters.command("pipes") & filters.user(SUDOERS))
@capture_err
async def show_pipes_func(_, message: Message):
    pipes_list_bot.update(pipes_list_userbot)
    if not pipes_list_bot:
        return await message.reply_text("pipe hi a active mek e.")

    text = ""
    for count, pipe in enumerate(pipes_list_bot.items(), 1):
        text += (
            f"**Pipe:** `{count}`\n**From:** `{pipe[0]}`\n"
            + f"**To:** `{pipe[1]}`\n\n"
        )
    await message.reply_text(text)
