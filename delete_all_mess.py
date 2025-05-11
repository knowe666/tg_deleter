import asyncio
from asyncio import sleep
from random import randint

from pyrogram import Client
from pyrogram.enums import ChatType, MessageEntityType


async def get_chats_from_bot(app):
    print("Запуск. Выгружаю группы из бота.")
    await app.send_message("@Kiss_my_data_bot", "/start")
    await sleep(randint(22, 33)/10)
    async for message in app.get_chat_history("@Kiss_my_data_bot", limit=1):
        if message.reply_markup:
            await message.click(0)
    await sleep(randint(22, 33)/10)
    await app.send_message("@Kiss_my_data_bot", "/me")
    await sleep(randint(22, 33)/10)
    async for message in app.get_chat_history("@Kiss_my_data_bot", limit=1):
        await message.click(3)
    await sleep(randint(22, 33)/10)
    all_groups = dict()
    while True:
        message = await app.get_messages("@Kiss_my_data_bot", message.id)
        for ent in message.entities:
            if ent.type == MessageEntityType.TEXT_LINK:
                try:
                    chat_data = await app.get_chat(ent.url)
                    await sleep(randint(10, 15) / 10)
                except:
                    continue
                if chat_data.type == ChatType.CHANNEL:
                    link = f"https://t.me/{chat_data.linked_chat.username}" if chat_data.linked_chat.username else f"https://t.me/c/{chat_data.linked_chat.id * -1 - 10 ** 12}"
                    all_groups[chat_data.linked_chat.id] = [chat_data.linked_chat.title, link]
                else:
                    link = f"https://t.me/{chat_data.username}" if chat_data.username else f"https://t.me/c/{chat_data.id * -1 - 10 ** 12}"
                    all_groups[chat_data.id] = [chat_data.title, link]
        if " \n|- " in message.text or "➡️" not in message.reply_markup.inline_keyboard[0][2].text or message.reply_markup.inline_keyboard.__len__() == 4:
            break
        await message.click(2)
        await sleep(randint(22, 33)/10)
    return all_groups


async def delete_message(app, chat):
    list_of_message_ids = []
    count = 0
    async for message in app.search_messages(chat[0], from_user="me"):
        list_of_message_ids.append(message.id)
    if list_of_message_ids:
        count = await app.delete_messages(chat[0], list_of_message_ids)
        if count != len(list_of_message_ids):
            print(f"Не удалось удалить {len(list_of_message_ids)-count} сообщений в {chat[3]}")
    return count


async def get_all_chat(app, groups_stats):
    print("Выгружаю группы из аккаунта.")
    chats = dict()
    async for dialog in app.get_dialogs(from_archive=True):
        if dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            count_mess = await app.search_messages_count(dialog.chat.id, from_user="me")
            if count_mess:
                link = f"https://t.me/{dialog.chat.username}" if dialog.chat.username else f"https://t.me/c/{dialog.chat.id * -1 - 10 ** 12}"
                chats[dialog.chat.id] = [dialog.chat.title, count_mess, link]
    for group in groups_stats:
        if group not in chats:
            count_mess = await app.search_messages_count(group, from_user="me")
            if count_mess:
                chats[group] = [groups_stats[group][0], count_mess, groups_stats[group][1]]
    return chats


async def main():
    async with Client("oleg") as app:
        groups_stats = await get_chats_from_bot(app)
        chats = await get_all_chat(app, groups_stats)
        chats = [[chat, *chats[chat]] for chat in chats]
        while True:
            if not chats:
                print("Групп с сообщениями не обнаружено.")
                return
            for i, chat in enumerate(chats):
                print(f"[{i+1}] {chat[1]} | Cообщений: {chat[2]} {chat[3]}")
            print("---------------------\n"
                  "## Отправьте номер чата, что бы убрать его из списка для удаления.\n"
                  "## Отправьте Y для запуска удаления сообщений.")
            answer = input()
            if answer in ["y", "Y", "н", "Н"]:
                all_mess = 0
                for chat in chats:
                    count = await delete_message(app, chat)
                    if count:
                        print(f"Удаленно {count} сообщений в {chat[1]}")
                        all_mess += count
                print(f"Всего удаленно {all_mess} сообщений.")
                return
            try:
                answer = int(answer)
            except:
                print("Неверный ввод. Оправьте число")
            else:
                del chats[answer-1]


asyncio.run(main())
