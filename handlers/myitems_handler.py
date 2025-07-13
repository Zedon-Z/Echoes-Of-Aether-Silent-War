elif text == "/myitems":
    inv = db.get_inventory(user_id)
    if not inv:
        safe_reply("🎒 Your inventory is empty.")
    else:
        buttons = [
            [InlineKeyboardButton(f"Use: {item} ({qty})", callback_data=f"useitem_{item}")]
            for item, qty in inv.items()
        ]

        context.bot.send_message(
            chat_id=user_id,
            text="🧰 *Your Items:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
