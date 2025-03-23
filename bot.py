from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = "8078550274:AAEp_DLqDdFZwK-nO0EIeHGO7DriS5Y92pg"

# �������� ������� � �� chat_id (��������, "@channelusername")
buttons = ["�����������", "����������", "FAQ", "�����"]
channels = ["@hant2025001", "@hant2025001", "@hant2025001", "@hant2025004"]  # Caiaieoa ia ?aaeuiua eaiaeu

# Iannea n message_id aey ea?aiai eaiaea
message_ids = [
    [2, 3, 4, 5,777],  # message_id  
    [6, 777],  # message_id  [22345, 22346, 22347],  # message_id aey eaiaea 2
    [6, 777],  # message_id  [32345, 32346, 32347]   # message_id aey eaiaea 3
    [2]
]

# GS �������� id ��������� / id ��������� �������� / ������� ������ � ���������� � �� ��� � �������_buttons / ID ��������� ��� �����
gslast = [777, 2, 4, 6 ]

# ��� �������� ������� ������� ���������
user_positions = {}

# ������� ��� �������� message_id ���������� ���������
previous_messages = {}

async def start(update, context):
    print("������� /start ��������")  # �����������

    try:#GS ������� ������� ����
        await update.message.delete()  # ������� ��������� ���������
    except Exception as e:
            print(f"�� ������� ������� ��������� ���������: {e}")

    #GS ��� ������������
    user = update.message.from_user
    # �������� ����� �����, ��������� ������ ��������
    name_parts = []
    if user.first_name:
        name_parts.append(user.first_name)
    #if user.last_name:        name_parts.append(user.last_name)
    # ��������� �������� ������
    full_name = " ".join(name_parts) if name_parts else ""

    
 #   keyboard = [[KeyboardButton(button)] for button in buttons]
    keyboard = [[buttons[0],buttons[1]],[buttons[2],buttons[3]]]

    reply_markup = ReplyKeyboardMarkup(keyboard,  one_time_keyboard=False, resize_keyboard=True)
    await update.message.reply_text(f"������������,: @{full_name}!", reply_markup=reply_markup)

    try:#GS ������ ��������� ����
    # �������� ��������� �� ������
        msg = await context.bot.copy_message(
            chat_id=update.effective_chat.id,
            from_chat_id=channels[gslast[2]-1],
            message_id=gslast[3]
        )
    except Exception as e:
        print(f"������ ��� ����������� ���������1: {e}")


async def button(update, context):
    print("������ ������:", update.message.text)  # �����������

    try:#GS ������� ������� ����
        await update.message.delete()  # ������� ��������� ���������
    except Exception as e:
            print(f"�� ������� ������� ��������� ���������: {e}")

    user_id = update.message.from_user.id
    # ������ ������ ������ �� ������ ������
    channel_index = buttons.index(update.message.text)

    # ��������� ������� ������ ������
    user_positions[user_id] = {"channel_index": channel_index, "message_index": 0}

    # ���������� ������ ��������� �� ���������� ������
    await send_message(update, context, user_id)

async def send_message(update, context, user_id):
    user_data = user_positions[user_id]
    channel_index = user_data["channel_index"]
    message_index = user_data["message_index"]
    channel = channels[channel_index]
    message_id = message_ids[channel_index][message_index]

    #GS ���� ��������� ��������� �� ��������� ��������� ���������
    if message_id == gslast[0] :
        channel = channels[gslast[2]-1]
        message_id =gslast[1]

    inline_keyboard = [
        [InlineKeyboardButton("�����", callback_data="back"),
         InlineKeyboardButton("�����", callback_data="next")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)

    chat_id = update.effective_chat.id

    # ������� ���������� ���������, ���� ��� ����������
    if user_id in previous_messages:
        prev_message_id = previous_messages[user_id]
        try:
            await context.bot.delete_message(chat_id, prev_message_id)
        except Exception as e:
            print(f"������ ��� �������� ���������: {e}")

    try:
        # �������� ��������� �� ������
        msg = await context.bot.copy_message(
            chat_id=chat_id,
            from_chat_id=channel,
            message_id=message_id
        )
        # ��������� message_id �������� ���������, ����� � ��������� ��� ��� �������
        previous_messages[user_id] = msg.message_id

        # ��������� ������-���������� � �������������� ���������
        await context.bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=msg.message_id,
            reply_markup=reply_markup
        )

    except Exception as e:
        print(f"������ ��� ����������� ���������: {e}")

async def navigation(update, context):
    print("���������: ", update.callback_query.data)  # �����������
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in user_positions:
        print(f"��� ������� ��� ������������ {user_id}")  # �����������
        return

    user_data = user_positions[user_id]
    channel_index = user_data["channel_index"]
    message_index = user_data["message_index"]

    if query.data == "next":
        if message_index < len(message_ids[channel_index]) - 1:
            user_positions[user_id]["message_index"] = message_index + 1
        else:
            user_positions[user_id]["message_index"] = 0  # ��������� �� ������ ���������
    elif query.data == "back":
        if message_index > 0:
            user_positions[user_id]["message_index"] = message_index - 1
        else:
      #      user_positions[user_id]["message_index"] = 0  # ��������� �� ��������� 
            user_positions[user_id]["message_index"] = len(message_ids[channel_index]) - 1  # ��������� �� ��������� ���������

    await send_message(update, context, user_id)

def main():
    print("������ ����...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button))
    application.add_handler(CallbackQueryHandler(navigation, pattern="^(next|back)$"))

    print("��� ��������� � ��������...")
    application.run_polling()

if __name__ == '__main__':
    print("������ polling...")
    main()  # ������ ����� main() ��� asyncio.run()
