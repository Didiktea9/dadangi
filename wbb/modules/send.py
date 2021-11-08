from pyrogram import filters


@app.on_message(filters.command("snd") & ~filters.edited)
async def send(_, message):
  rsr = message.text.split(None, 1)[1]
  if not rsr:
    await message.reply_text("Thawn tur dah tel rawh")
    return
  await app.send_message(rsr, disable_web_page_preview=True)
  await message.delete()
