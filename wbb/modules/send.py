from pyrogram import filters
from wbb import app
from wbb.core.decorators.errors import capture_err

@app.on_message(filters.command("snd"))
@capture_err
async def send(_, message):
  rsr = message.text.split(None, 1)[1]
  await app.send_message(message.chat.id, text=rsr, disable_web_page_preview=True)
  await message.delete()
