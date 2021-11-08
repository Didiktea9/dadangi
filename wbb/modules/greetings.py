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
import os
from datetime import datetime
from random import shuffle

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (ChatAdminRequired,
                                                        UserNotParticipant)
from pyrogram.types import (Chat, ChatPermissions, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message, User)

from wbb import SUDOERS, WELCOME_DELAY_KICK_SEC, app
from wbb.core.decorators.errors import capture_err
from wbb.core.decorators.permissions import adminsOnly
from wbb.core.keyboard import ikb
from wbb.utils.dbfunctions import (captcha_off, captcha_on, del_welcome,
                                   get_captcha_cache, get_welcome,
                                   has_solved_captcha_once, is_captcha_on,
                                   is_gbanned_user, save_captcha_solved,
                                   set_welcome, update_captcha_cache)
from wbb.utils.filter_groups import welcome_captcha_group
from wbb.utils.functions import extract_text_and_keyb, generate_captcha

__MODULE__ = "Greetings"
__HELP__ = """
➤/captcha [ENABLE|DISABLE] - Captcha on na leh off na.

➤/setwelcome - Welcome message tur a i duh kha format diktak in type la,chu chu command hmang sawn i reply dawn nia. 

➤/delwelcome - Welcome message delete na.
➤/getwelcome - Welcome message set mek en na.

**SET_WELCOME ->**

**A format chu  a hnuai ami ang hian i set dawn nia.**

```
**Hi** {name} Welcome to {chat}

~ 
     He sign (~) hi text leh button then hrangtu tur ani a,  (~) hemi sign tello hi chuan welcome i set dik theilo ang

button=[Duck, https://duckduckgo.com]
button2=[Github, https://github.com]
```

**NOTES ->**

/rules atan bik chuan, /filter rules tih pawh a hmantheih
tho bawk.I group members ten he
/rules tih hi an thawn apiangin, an hmu thei ang

A hnuai a /markdownhelp khu formatting and syntax dik leh dikloh i hriat theih nan chhiar ang che.
"""


answers_dicc = []
loop = asyncio.get_running_loop()


async def get_initial_captcha_cache():
    global answers_dicc
    answers_dicc = await get_captcha_cache()
    return answers_dicc


loop.create_task(get_initial_captcha_cache())


@app.on_message(filters.new_chat_members, group=welcome_captcha_group)
@capture_err
async def welcome(_, message: Message):
    global answers_dicc

    # Get cached answers from mongodb in case of bot's been restarted or crashed.
    answers_dicc = await get_captcha_cache()

    # Mute new member and send message with button
    if not await is_captcha_on(message.chat.id):
        return

    for member in message.new_chat_members:
        try:

            if member.id in SUDOERS:
                continue  # ignore sudo users

            if await is_gbanned_user(member.id):
                await message.chat.kick_member(member.id)
                await message.reply_text(
                    f"{member.mention} chu global banned leh removed ani e,"
                    + " He thil hi tihsual palh avanga gban ni a i hriat chuan, support Group"
                    + " ah ilo sawi dawn nia."
                )
                continue

            if member.is_bot:
                continue  # ignore bots

            # Ignore user if he has already solved captcha in this group
            # someday
            if await has_solved_captcha_once(message.chat.id, member.id):
                continue

            await message.chat.restrict_member(member.id, ChatPermissions())
            text = (
                f"**Duhtak {(member.mention())} Mihring i ni ngei em fiah lawk ang aw** !\n\n"
                f"**Thlalak a thil inziak hi a hnuai ami ah khuan {WELCOME_DELAY_KICK_SEC}** "
                "**seconds (5min) chhung a i hmet hmanlo emaw vawi 4 i tidiklo anih chuan Bot in a kick ang che**."
            )
        except ChatAdminRequired:
            return
        # Generate a captcha image, answers and some wrong answers
        captcha = generate_captcha()
        captcha_image = captcha[0]
        captcha_answer = captcha[1]
        wrong_answers = captcha[2]  # This consists of 8 wrong answers
        correct_button = InlineKeyboardButton(
            f"{captcha_answer}",
            callback_data=f"pressed_button {captcha_answer} {member.id}",
        )
        temp_keyboard_1 = [correct_button]  # Button row 1
        temp_keyboard_2 = []  # Botton row 2
        temp_keyboard_3 = []
        for i in range(2):
            temp_keyboard_1.append(
                InlineKeyboardButton(
                    f"{wrong_answers[i]}",
                    callback_data=f"pressed_button {wrong_answers[i]} {member.id}",
                )
            )
        for i in range(2, 5):
            temp_keyboard_2.append(
                InlineKeyboardButton(
                    f"{wrong_answers[i]}",
                    callback_data=f"pressed_button {wrong_answers[i]} {member.id}",
                )
            )
        for i in range(5, 8):
            temp_keyboard_3.append(
                InlineKeyboardButton(
                    f"{wrong_answers[i]}",
                    callback_data=f"pressed_button {wrong_answers[i]} {member.id}",
                )
            )

        shuffle(temp_keyboard_1)
        keyboard = [temp_keyboard_1, temp_keyboard_2, temp_keyboard_3]
        shuffle(keyboard)
        verification_data = {
            "chat_id": message.chat.id,
            "user_id": member.id,
            "answer": captcha_answer,
            "keyboard": keyboard,
            "attempts": 0,
        }
        keyboard = InlineKeyboardMarkup(keyboard)
        # Append user info, correct answer and
        answers_dicc.append(verification_data)
        # keyboard for later use with callback query
        button_message = await message.reply_photo(
            photo=captcha_image,
            caption=text,
            reply_markup=keyboard,
            quote=True,
        )
        os.remove(captcha_image)

        # Save captcha answers etc in mongodb in case bot gets crashed or restarted.
        await update_captcha_cache(answers_dicc)

        asyncio.create_task(
            kick_restricted_after_delay(
                WELCOME_DELAY_KICK_SEC, button_message, member
            )
        )
        await asyncio.sleep(0.5)


async def send_welcome_message(chat: Chat, user_id: int):
    raw_text = await get_welcome(chat.id)

    if not raw_text:
        return

    text, keyb = extract_text_and_keyb(ikb, raw_text)

    if "{chat}" in text:
        text = text.replace("{chat}", chat.title)
    if "{name}" in text:
        text = text.replace("{name}", (await app.get_users(user_id)).mention)

    await app.send_message(
        chat.id,
        text=text,
        reply_markup=keyb,
        disable_web_page_preview=True,
    )


@app.on_callback_query(filters.regex("pressed_button"))
async def callback_query_welcome_button(_, callback_query):
    """After the new member presses the correct button,
    set his permissions to chat permissions,
    delete button message and join message.
    """
    global answers_dicc
    data = callback_query.data
    pressed_user_id = callback_query.from_user.id
    pending_user_id = int(data.split(None, 2)[2])
    button_message = callback_query.message
    answer = data.split(None, 2)[1]
    if len(answers_dicc) != 0:
        for i in answers_dicc:
            if (
                i["user_id"] == pending_user_id
                and i["chat_id"] == button_message.chat.id
            ):
                correct_answer = i["answer"]
                keyboard = i["keyboard"]

    if pending_user_id != pressed_user_id:
        return await callback_query.answer("Hei hi chu i ti ve theilo")

    if answer != correct_answer:
        await callback_query.answer("Aw, a diklo.")
        for iii in answers_dicc:
            if (
                iii["user_id"] == pending_user_id
                and iii["chat_id"] == button_message.chat.id
            ):
                attempts = iii["attempts"]
                if attempts >= 3:
                    answers_dicc.remove(iii)
                    await button_message.chat.kick_member(pending_user_id)
                    await asyncio.sleep(1)
                    await button_message.chat.unban_member(pending_user_id)
                    await button_message.delete()
                    await update_captcha_cache(answers_dicc)
                    return

                iii["attempts"] += 1
                break

        shuffle(keyboard[0])
        shuffle(keyboard[1])
        shuffle(keyboard[2])
        shuffle(keyboard)
        keyboard = InlineKeyboardMarkup(keyboard)
        return await button_message.edit(
            text=button_message.caption.markdown,
            reply_markup=keyboard,
        )

    await callback_query.answer("Captcha i ti dik e!")
    await button_message.chat.unban_member(pending_user_id)
    await button_message.delete()

    if len(answers_dicc) != 0:
        for ii in answers_dicc:
            if (
                ii["user_id"] == pending_user_id
                and ii["chat_id"] == button_message.chat.id
            ):
                answers_dicc.remove(ii)
                await update_captcha_cache(answers_dicc)

    chat = callback_query.message.chat

    # Save this verification in db, so we don't have to
    # send captcha to this user when he joins again.
    await save_captcha_solved(chat.id, pending_user_id)

    return await send_welcome_message(chat, pending_user_id)


async def kick_restricted_after_delay(
    delay, button_message: Message, user: User
):
    """If the new member is still restricted after the delay, delete
    button message and join message and then kick him
    """
    global answers_dicc
    await asyncio.sleep(delay)
    join_message = button_message.reply_to_message
    group_chat = button_message.chat
    user_id = user.id
    await join_message.delete()
    await button_message.delete()
    if len(answers_dicc) != 0:
        for i in answers_dicc:
            if i["user_id"] == user_id:
                answers_dicc.remove(i)
                await update_captcha_cache(answers_dicc)
    await _ban_restricted_user_until_date(group_chat, user_id, duration=delay)


async def _ban_restricted_user_until_date(
    group_chat, user_id: int, duration: int
):
    try:
        member = await group_chat.get_member(user_id)
        if member.status == "restricted":
            until_date = int(datetime.utcnow().timestamp() + duration)
            await group_chat.kick_member(user_id, until_date=until_date)
    except UserNotParticipant:
        pass


@app.on_message(filters.command("captcha") & ~filters.private)
@adminsOnly("can_restrict_members")
async def captcha_state(_, message):
    usage = "**Usage:**\n/captcha [ENABLE|DISABLE]"
    if len(message.command) != 2:
        await message.reply_text(usage)
        return
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        await captcha_on(chat_id)
        await message.reply_text("Members thar tan Captcha on na.")
    elif state == "disable":
        await captcha_off(chat_id)
        await message.reply_text("Members thar tan Captcha off na.")
    else:
        await message.reply_text(usage)


# WELCOME MESSAGE


@app.on_message(filters.command("setwelcome") & ~filters.private)
@adminsOnly("can_change_info")
async def set_welcome_func(_, message):
    usage = "Thuziak reply i neih angai, Greetings module ah khan a tihdan kan sawi tawh kha"
    if not message.reply_to_message:
        await message.reply_text(usage)
        return
    if not message.reply_to_message.text:
        await message.reply_text(usage)
        return
    chat_id = message.chat.id
    raw_text = message.reply_to_message.text.markdown
    if not (extract_text_and_keyb(ikb, raw_text)):
        return await message.reply_text("Format diklo i hmang, Chhiar chiang hram rawh.")
    await set_welcome(chat_id, raw_text)
    await message.reply_text("**Hlawhtling takin Welcome message set ani e.**")


@app.on_message(filters.command("delwelcome") & ~filters.private)
@adminsOnly("can_change_info")
async def del_welcome_func(_, message):
    chat_id = message.chat.id
    await del_welcome(chat_id)
    await message.reply_text("**Welcome message deleted ani e.**")


@app.on_message(filters.command("getwelcome") & ~filters.private)
@adminsOnly("can_change_info")
async def get_welcome_func(_, message):
    chat = message.chat
    welcome = await get_welcome(chat.id)
    if not welcome:
        return await message.reply_text("**Group ah hian Welcome message set a la nilo.**")
    if not message.from_user:
        return await message.reply_text(
            "Bengtulul, welcome message a en theihloh."
        )

    await send_welcome_message(chat, message.from_user.id)

    await message.reply_text(f'`{welcome.replace("`", "")}`')
