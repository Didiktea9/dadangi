@app.on_message(filters.command("Lynn") & ~filters.edited)
async def asq(_, message):
