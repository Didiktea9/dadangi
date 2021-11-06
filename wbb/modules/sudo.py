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
from pyrogram import filters
from pyrogram.types import Message

from wbb import BOT_ID, SUDOERS, USERBOT_PREFIX, app2, eor
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfunctions import add_sudo, get_sudoers, remove_sudo
from wbb.utils.functions import restart

__MODULE__ = "Sudo"
__HELP__ = """
**HE MODULE HI CHU DEVS HO TAN BIK ANI**

➤.useradd - Sudoers a mi add na.
➤.userdel - Sudoers atang a mi paihna.
➤.sudoers - Sudo Users list en na.

**NOTE:**

Tumah Sudoers ah hian add ringawt suh i ringtawk hle te anih loh chuan,
sudo users hian i account ah engpawh an ti thei vek a, an duh chuan
i account pawh an delete thei.
"""


@app2.on_message(
    filters.command("useradd", prefixes=USERBOT_PREFIX) & filters.user(SUDOERS)
)
@capture_err
async def useradd(_, message: Message):
    if not message.reply_to_message:
        return await eor(
            message,
            text="Sudoers a add tur chuan an message i reply tel angai.",
        )
    user_id = message.reply_to_message.from_user.id
    umention = (await app2.get_users(user_id)).mention
    sudoers = await get_sudoers()
    if user_id in sudoers:
        return await eor(message, text=f"{umention} is already in sudoers.")
    if user_id == BOT_ID:
        return await eor(
            message, text="Sudoers ah hi chuan bot asssistant a add theih loh."
        )
    added = await add_sudo(user_id)
    if added:
        await eor(
            message,
            text=f"Hlawhtling takin {umention} chu sudoers ah add ani e, Bot hi a in restart nghal ang.",
        )
        return await restart(None)
    await eor(message, text="Something wrong happened, check logs.")


@app2.on_message(
    filters.command("userdel", prefixes=USERBOT_PREFIX) & filters.user(SUDOERS)
)
@capture_err
async def userdel(_, message: Message):
    if not message.reply_to_message:
        return await eor(
            message,
            text="Reply to someone's message to remove him to sudoers.",
        )
    user_id = message.reply_to_message.from_user.id
    umention = (await app2.get_users(user_id)).mention
    if user_id not in await get_sudoers():
        return await eor(message, text=f"{umention} is not in sudoers.")
    removed = await remove_sudo(user_id)
    if removed:
        await eor(
            message,
            text=f"Hlawhtling takin {umention} chu sudoers atang delete ani e, Bot a in restart nghal ang.",
        )
        return await restart(None)
    await eor(message, text="Something wrong happened, check logs.")


@app2.on_message(
    filters.command("sudoers", prefixes=USERBOT_PREFIX) & filters.user(SUDOERS)
)
@capture_err
async def sudoers_list(_, message: Message):
    sudoers = await get_sudoers()
    text = ""
    for count, user_id in enumerate(sudoers, 1):
        user = await app2.get_users(user_id)
        user = user.first_name if not user.mention else user.mention
        text += f"{count}. {user}\n"
    await eor(message, text=text)
