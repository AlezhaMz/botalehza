import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import os

# ========== НАСТРОЙКИ (ЗАМЕНИ НА СВОИ) ==========
BOT_TOKEN = "8762058651:AAG_rvoUoqFY3Be13ueYk32I-2Jriwxecn4"  # Получи у @BotFather
GROUP_ID = -1003666056371        # ID твоей группы
ADMIN_IDS = [1487417026]         # Твой Telegram ID
# ====================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== ДАННЫЕ ДЛЯ СТАТИСТИКИ ==========
daily_messages = defaultdict(int)
daily_new_members = 0
today = datetime.now().date()

# ========== ДАННЫЕ ДЛЯ АНТИ-СПАМА ==========
user_last_msg = {}
user_warns = {}
warnings = {}

# ========== ВАШ FILE_ID ==========
PHOTO_1 = "AgACAgIAAyEFAATag5SzAAJcEWpbwBfRU_d2Xt7ep9khEBTSu0ivAALEGmsb0szYSrjC4egU1-QRAQADAgADeAADPQQ"
PHOTO_2 = "AgACAgIAAyEFAATag5SzAAJcE2pbwG-94ZnFIjWKlJxqWEcmzFVVAALFGmsb0szYStdVM3dCKHIlAQADAgADeAADPQQ"
PHOTO_3 = "AgACAgIAAyEFAATag5SzAAJcFWpbwIx5YjYhv-bziCsowKQoxpFdAALGGmsb0szYSvVuzTH8ZpKBAQADAgADeQADPQQ"
PHOTO_4 = "AgACAgIAAyEFAATag5SzAAJcF2pbwLQBwd2W4EY_eZPzaKa4iTYAA8caaxvSzNhKKLMsL1sruBEBAAMCAAN5AAM9BA"

# ========== ПЕРИОДИЧЕСКИЕ СООБЩЕНИЯ С ФОТО ==========
PERIODIC_CONTENT = [
    {
        "text": "➤ Больше контента в других форматах!\nСмотри развлекательный контент по Dota 2 в наших YouTube и TikTok аккаунтах.\n➤ <a href='https://youtube.com/@shopkeeperscache?si=aXYmxlKyxbo422Wb'>Перейти в YouTube</a>\n➤ <a href='https://www.tiktok.com/@shopkeeperscache?_r=1&_t=ZS-986eaBQ3xOn'>Перейти в TikTok</a>",
        "file_id": PHOTO_1
    },
    {
        "text": "➤ Не пропусти новые скидки и актуальные новости!\nПодписывайся на наш Telegram-канал «Тайны Торговца» — здесь всё появляется первым.\nЖми на <a href='https://t.me/StashShopkeepers'>ссылку</a> и будь в плюсе! 🔥",
        "file_id": PHOTO_2
    },
    {
        "text": "➤ Общайтесь, торгуйте, находите тиммейтов для Dota 2 — у нас уютно всем!\nА если заметите нарушение правил чата — не молчите, сразу сообщите @AIezha. Вместе сделаем сообщество лучше! 🤝",
        "file_id": PHOTO_3
    },
    {
        "text": "➤ Ищете, с кем зарубиться в Dota 2?\nУ нас уютный Discord-сервер, где всегда найдётся пати, поддержка и хорошее настроение.\nЖдём тебя! Заходи в наш <a href='https://discord.gg/AtQypC6jK'>Discord-сервер</a>",
        "file_id": PHOTO_4
    }
]

# ========== ПРИВЕТСТВИЕ НОВЫХ УЧАСТНИКОВ ==========
@dp.message(F.content_type == types.ContentType.NEW_CHAT_MEMBERS)
async def welcome_new_members(message: types.Message):
    global daily_new_members, today
    
    now = datetime.now().date()
    if now != today:
        today = now
        daily_new_members = 0
        daily_messages.clear()
    
    for user in message.new_chat_members:
        if user.id == bot.id:
            continue
        
        # Блокировка ботов
        if user.is_bot:
            try:
                await bot.ban_chat_member(GROUP_ID, user.id)
                await message.answer(f"🚫 Бот {user.full_name} удалён!")
            except:
                pass
            continue
        
        daily_new_members += 1
        
        # Приветствие с ссылкой на профиль
        greeting = (
            f"👋 Приветствуем <a href='tg://user?id={user.id}'>{user.full_name}</a>, в Лавке Главного Торговца! Можешь пообщаться с нами в чате или\n"
            f"➤ <a href='https://t.me/ShopkeepersCache/17163'>Узнать о нас подробнее</a>\n"
            f"➤ <a href='https://t.me/ShopkeepersCache'>Ознакомится с каталогом лавки</a>\n"
            f"➤ <a href='https://t.me/StashShopkeepers'>Зайти в Тайник Торговца</a>"
        )
        try:
            await message.answer(greeting, parse_mode="HTML", disable_web_page_preview=True)
        except:
            pass
    
    # Удаляем системное сообщение
    try:
        await message.delete()
    except:
        pass

# ========== УДАЛЕНИЕ СООБЩЕНИЙ О ВЫХОДЕ ==========
@dp.message(F.content_type == types.ContentType.LEFT_CHAT_MEMBER)
async def delete_left_message(message: types.Message):
    try:
        await message.delete()
    except:
        pass

# ========== ПОДСЧЁТ СООБЩЕНИЙ ДЛЯ СТАТИСТИКИ ==========
@dp.message(F.text)
async def count_messages(message: types.Message):
    if message.chat.id != GROUP_ID:
        return
    if message.from_user.is_bot or message.from_user.id in ADMIN_IDS:
        return
    daily_messages[message.from_user.id] += 1

# ========== АНТИ-СПАМ ==========
@dp.message(F.text)
async def anti_spam(message: types.Message):
    if message.chat.id != GROUP_ID:
        return
    
    if message.from_user.id in ADMIN_IDS or message.from_user.is_bot:
        return
    
    user_id = message.from_user.id
    now = datetime.now()
    
    if user_id in user_last_msg:
        time_diff = (now - user_last_msg[user_id]).seconds
        if time_diff < 5:
            user_warns[user_id] = user_warns.get(user_id, 0) + 1
            if user_warns[user_id] >= 3:
                await bot.ban_chat_member(GROUP_ID, user_id)
                await message.answer(f"🚫 {message.from_user.full_name} забанен за спам!")
                del user_last_msg[user_id]
                del user_warns[user_id]
                return
            else:
                await message.delete()
                await message.answer(f"⚠️ {message.from_user.full_name}, не спамь! Предупреждение {user_warns[user_id]}/3")
                return
        else:
            user_warns[user_id] = 0
    user_last_msg[user_id] = now

# ========== /mute - ОТКЛЮЧИТЬ ЗВУК НА 5 МИНУТ ==========
@dp.message(Command('mute'))
async def mute_user(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Только для админов!")
        return
    
    if not message.reply_to_message:
        await message.answer("❌ Ответь на сообщение пользователя!")
        return
    
    user_id = message.reply_to_message.from_user.id
    chat_member = await bot.get_chat_member(GROUP_ID, user_id)
    
    if chat_member.status in ["administrator", "creator"]:
        await message.answer("❌ Нельзя замутить администратора!")
        return
    
    until_date = datetime.now() + timedelta(minutes=5)
    
    try:
        await bot.restrict_chat_member(
            GROUP_ID, 
            user_id, 
            until_date=until_date,
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )
        await message.answer(f"🔇 {message.reply_to_message.from_user.first_name} замучен на 5 минут!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)[:100]}")

# ========== /ban - ЗАБАНИТЬ ==========
@dp.message(Command('ban'))
async def ban_user(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Только для админов!")
        return
    
    if not message.reply_to_message:
        await message.answer("❌ Ответь на сообщение пользователя!")
        return
    
    user_id = message.reply_to_message.from_user.id
    chat_member = await bot.get_chat_member(GROUP_ID, user_id)
    
    if chat_member.status in ["administrator", "creator"]:
        await message.answer("❌ Нельзя забанить администратора!")
        return
    
    try:
        await bot.ban_chat_member(GROUP_ID, user_id)
        await message.answer(f"🚫 {message.reply_to_message.from_user.first_name} забанен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)[:100]}")

# ========== /warn - ПРЕДУПРЕЖДЕНИЕ ==========
@dp.message(Command('warn'))
async def warn_user(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Только для админов!")
        return
    
    if not message.reply_to_message:
        await message.answer("❌ Ответь на сообщение пользователя!")
        return
    
    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.first_name
    
    if user_id in ADMIN_IDS:
        await message.answer("❌ Нельзя выдать предупреждение администратору!")
        return
    
    warnings[user_id] = warnings.get(user_id, 0) + 1
    warn_count = warnings[user_id]
    
    await message.answer(f"⚠️ {user_name} получил предупреждение! ({warn_count}/3)")
    
    if warn_count >= 3:
        try:
            await bot.ban_chat_member(GROUP_ID, user_id)
            await message.answer(f"🚫 {user_name} забанен за 3 предупреждения!")
            del warnings[user_id]
        except:
            pass

# ========== ФУНКЦИЯ ОТПРАВКИ С ИЗОБРАЖЕНИЯМИ ==========
async def send_periodic_content(content):
    """Отправляет сообщение с изображением из локального файла"""
    try:
        if content.get("local_file") and os.path.exists(content["local_file"]):
            with open(content["local_file"], "rb") as photo:
                msg = await bot.send_photo(
                    chat_id=GROUP_ID,
                    photo=photo,
                    caption=content["text"],
                    parse_mode="HTML"
                )
            return msg
    except Exception as e:
        print(f"Ошибка отправки фото: {e}")
    
    # Если ошибка - отправляем только текст
    msg = await bot.send_message(
        chat_id=GROUP_ID,
        text=content["text"],
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    return msg

# ========== ПЕРИОДИЧЕСКИЕ СООБЩЕНИЯ ==========
async def periodic_messages():
    index = 0
    last_msg_ids = []
    
    while True:
        try:
            now = datetime.now()
            if 5 <= now.hour < 19:
                # Удаляем предыдущие сообщения
                for msg_id in last_msg_ids:
                    try:
                        await bot.delete_message(GROUP_ID, msg_id)
                    except:
                        pass
                last_msg_ids.clear()
                
                content = PERIODIC_CONTENT[index % len(PERIODIC_CONTENT)]
                msg = await send_periodic_content(content)
                last_msg_ids.append(msg.message_id)
                
                index += 1
                await asyncio.sleep(7200)
            else:
                await asyncio.sleep(60)
        except Exception as e:
            print(f"Ошибка в periodic: {e}")
            await asyncio.sleep(60)

# ========== УТРЕННЕЕ ПРИВЕТСТВИЕ В 05:00 ==========
async def daily_greetings():
    last_greeting = None
    last_farewell = None
    while True:
        try:
            now = datetime.now()
            
            # Утро в 05:00
            if now.hour == 5 and now.minute == 0 and last_greeting != now.date():
                await bot.send_message(
                    GROUP_ID,
                    "Всем привет! Выспался, зарядился и снова в строю! ☀️\n"
                    "➤ Рассвет встретил, слово сдержал. Доброе утро, народ!\n"
                    "➤ Без меня скучали? Признавайтесь!\n"
                    "➤ Готовься - сегодня будет интересно, я обещаю...",
                    parse_mode="HTML"
                )
                last_greeting = now.date()
                await asyncio.sleep(60)
            
            # Вечер в 19:00
            if now.hour == 19 and now.minute == 0 and last_farewell != now.date():
                await bot.send_message(
                    GROUP_ID,
                    "Всем бай-бай! Отключаюсь до утра, чтобы дать вашим уведомлениям отдохнуть. 😴\n"
                    "➤ Не шалите пока меня нет!\n"
                    "➤ Завтра я открою для тебя новые тайны...\n"
                    "➤ Встретимся на первых лучах солнца. Сладких снов!",
                    parse_mode="HTML"
                )
                last_farewell = now.date()
                await asyncio.sleep(60)
            
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Ошибка в greetings: {e}")
            await asyncio.sleep(60)

# ========== КОМАНДА ДЛЯ ТЕСТА ==========
@dp.message(Command('test_all'))
async def test_all_messages(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Только для админов!")
        return
    
    await message.answer("🔄 Тест всех сообщений с фото...")
    
    for i, content in enumerate(PERIODIC_CONTENT, 1):
        try:
            if content.get("local_file") and os.path.exists(content["local_file"]):
                with open(content["local_file"], "rb") as photo:
                    await message.answer_photo(
                        photo=photo,
                        caption=f"📨 {i}:\n\n{content['text']}",
                        parse_mode="HTML"
                    )
            else:
                await message.answer(
                    f"📨 {i}:\n\n{content['text']}",
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
            await asyncio.sleep(1)
        except Exception as e:
            await message.answer(f"❌ Ошибка в {i}: {str(e)[:100]}")
    
    await message.answer("✅ Тест завершен!")

# ========== КОМАНДА ДЛЯ ПРОСМОТРА ФАЙЛОВ ==========
@dp.message(Command('list_files'))
async def list_files(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    files = os.listdir('.')
    text = "📁 Файлы в папке бота:\n\n"
    for f in sorted(files):
        if os.path.isfile(f):
            size = os.path.getsize(f)
            text += f"• {f} ({size} байт)\n"
    await message.answer(text[:4000])

# ========== ПОЛУЧЕНИЕ FILE_ID ==========
@dp.message(F.photo)
async def get_file_id(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        file_id = message.photo[-1].file_id
        await message.reply(
            f"📸 File ID:\n<code>{file_id}</code>",
            parse_mode="HTML"
        )

# ========== ЗАПУСК ==========
async def main():
    print("=" * 50)
    print("🛡 БОТ ЗАПУЩЕН!")
    print("=" * 50)
    print("✅ Приветствие с ссылкой на профиль")
    print("✅ /ban, /mute, /warn для админов")
    print("✅ Анти-спам (бан за 3 сообщения за 5 секунд)")
    print("✅ Утро в 05:00, Вечер в 19:00")
    print("✅ Периодические сообщения с фото каждые 2 часа")
    print("")
    print("📁 Используются файлы:")
    for i, content in enumerate(PERIODIC_CONTENT, 1):
        print(f"  {i}. {content.get('local_file', 'Нет файла')}")
    print("=" * 50)
    print("✅ /test_all - тест всех сообщений")
    print("✅ /list_files - список файлов")
    print("=" * 50)
    
    asyncio.create_task(periodic_messages())
    asyncio.create_task(daily_greetings())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
