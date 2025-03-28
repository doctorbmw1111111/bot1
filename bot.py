﻿# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import os
import threading
from flask import Flask  # ### WEB SERVER START: Импорт Flask

TOKEN = "8078550274:AAEp_DLqDdFZwK-nO0EIeHGO7DriS5Y92pg"

# Названия каналов и их chat_id (например, "@channelusername")
buttons = ["Презентация", "Инструкция", "FAQ", "Связь"]
channels = ["@hant2025001", "@hant2025001", "@hant2025001", "@hant2025004"]  # Caiaieoa ia ?aaeuiua eaiaeu

# Iannea n message_id aey ea?aiai eaiaea
message_ids = [
    [2, 3, 4, 5, 777],  # message_id  
    [6, 777],  # message_id
    [6, 777],  # message_id
    [2]
]

# GS условное id сообщения / id сообщения реальное / порядок канала с контактами и др инф в массиве_buttons / ID сообщения для старт
gslast = [777, 2, 4, 6]

# Для хранения текущих позиций сообщений
user_positions = {}

# Словарь для хранения message_id предыдущих сообщений
previous_messages = {}

async def start(update, context):
    print("Команда /start получена")  # Логирование

    try:
        await update.message.delete()  # Удаляем командное сообщение
    except Exception as e:
        print(f"Не удалось удалить командное сообщение: {e}")

    user = update.message.from_user
    name_parts = []
    if user.first_name:
        name_parts.append(user.first_name)
    full_name = " ".join(name_parts) if name_parts else ""

    keyboard = [[buttons[0], buttons[1]], [buttons[2], buttons[3]]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text(f"Здравствуйте, @{full_name}!", reply_markup=reply_markup)

    try:
        msg = await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=channels[gslast[2]-1],
            message_id=gslast[3]
        )
    except Exception as e:
        print(f"Ошибка при копировании сообщения1: {e}")

async def button(update, context):
    print("Кнопка нажата:", update.message.text)  # Логирование

    try:
        await update.message.delete()  # Удаляем командное сообщение
    except Exception as e:
        print(f"Не удалось удалить командное сообщение: {e}")

    user_id = update.message.from_user.id
    channel_index = buttons.index(update.message.text)
    user_positions[user_id] = {"channel_index": channel_index, "message_index": 0}
    await send_message(update, context, user_id)

async def send_message(update, context, user_id):
    user_data = user_positions[user_id]
    channel_index = user_data["channel_index"]
    message_index = user_data["message_index"]
    channel = channels[channel_index]
    message_id = message_ids[channel_index][message_index]

    if message_id == gslast[0]:
        channel = channels[gslast[2]-1]
        message_id = gslast[1]

    inline_keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back"),
         InlineKeyboardButton("Далее", callback_data="next")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    chat_id = update.effective_chat.id

    if user_id in previous_messages:
        prev_message_id = previous_messages[user_id]
        try:
            await context.bot.delete_message(chat_id, prev_message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")

    try:
        msg = await context.bot.copy_message(
            chat_id=chat_id,
            from_chat_id=channel,
            message_id=message_id
        )
        previous_messages[user_id] = msg.message_id
        await context.bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=msg.message_id,
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Ошибка при копировании сообщения: {e}")

async def navigation(update, context):
    print("Навигация: ", update.callback_query.data)  # Логирование
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_positions:
        print(f"Нет позиции для пользователя {user_id}")  # Логирование
        return

    user_data = user_positions[user_id]
    channel_index = user_data["channel_index"]
    message_index = user_data["message_index"]

    if query.data == "next":
        if message_index < len(message_ids[channel_index]) - 1:
            user_positions[user_id]["message_index"] = message_index + 1
        else:
            user_positions[user_id]["message_index"] = 0  # Зациклили на первое сообщение
    elif query.data == "back":
        if message_index > 0:
            user_positions[user_id]["message_index"] = message_index - 1
        else:
            user_positions[user_id]["message_index"] = len(message_ids[channel_index]) - 1  # Зациклили на последнее сообщение

    await send_message(update, context, user_id)

### WEB SERVER START: Минимальный веб-сервер для открытия порта (Render)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

def run_webserver():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
### WEB SERVER END

def main():
    print("Запуск бота...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button))
    application.add_handler(CallbackQueryHandler(navigation, pattern="^(next|back)$"))

    # Запускаем веб-сервер в отдельном потоке, чтобы открыть порт для Render
    threading.Thread(target=run_webserver).start()
    
    print("Бот подключен и работает...")
    application.run_polling()

if __name__ == '__main__':
    print("Запуск polling...")
    main()  # Прямой вызов main() без asyncio.run()
