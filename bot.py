import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

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
warnings = {}

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

# ========== ПЕРИОДИЧЕСКИЕ СООБЩЕНИЯ ==========
MESSAGES = [
    "➤ Ищете, с кем зарубиться в Dota 2?\nУ нас уютный Discord-сервер, где всегда найдётся пати, поддержка и хорошее настроение.\nЖдём тебя! Заходи в наш <a href='https://discord.gg/AtQypC6jK'>Discord-сервер</a>",
    "➤ Не пропусти новые скидки и актуальные новости!\nПодписывайся на наш Telegram-канал «Тайны Торговца» — здесь всё появляется первым.\nЖми на <a href='https://t.me/StashShopkeepers'>ссылку</a> и будь в плюсе! 🔥",
    "➤ Общайтесь, торгуйте, находите тиммейтов для Dota 2 — у нас уютно всем!\nА если заметите нарушение правил чата — не молчите, сразу сообщите @AIezha. Вместе сделаем сообщество лучше! 🤝"
    "➤ Больше контента в других форматах!\nСмотри развлекательный контент по Dota 2 в наших YouTube и TikTok\n➤ <a href='https://youtube.com/@shopkeeperscache?si=aXYmxlKyxbo422Wb'>Перейти в YouTube</a>\n➤ <a href='https://www.tiktok.com/@shopkeeperscache?_r=1&_t=ZS-986eaBQ3xOn'>Перейти в TikTok</a>"
]

async def periodic_messages():
    index = 0
    last_msg_id = None
    while True:
        try:
            now = datetime.now()
            if 5 <= now.hour < 19:
                if last_msg_id:
                    try:
                        await bot.delete_message(GROUP_ID, last_msg_id)
                    except:
                        pass
                msg = await bot.send_message(
                    GROUP_ID,
                    MESSAGES[index % len(MESSAGES)],
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                last_msg_id = msg.message_id
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

# ========== СТАТИСТИКА В 19:00 ==========
async def daily_stats():
    global daily_messages, daily_new_members, today
    while True:
        try:
            now = datetime.now()
            if now.hour == 19 and now.minute == 0:
                members = await bot.get_chat_member_count(GROUP_ID)
                top_user = "Нет сообщений"
                top_count = 0
                if daily_messages:
                    top_id = max(daily_messages, key=daily_messages.get)
                    top_count = daily_messages[top_id]
                    try:
                        user = await bot.get_chat(top_id)
                        top_user = user.first_name or "Неизвестный"
                    except:
                        top_user = "Неизвестный"
                stats = (
                    f"📊 <b>Статистика за сегодня</b>\n\n"
                    f"👥 Участников: {members}\n"
                    f"💬 Сообщений: {sum(daily_messages.values())}\n"
                    f"🆕 Новых: {daily_new_members}\n"
                    f"🏆 Самый активный: {top_user} ({top_count} сообщений)\n"
                    f"📅 {now.strftime('%d.%m.%Y')}"
                )
                await bot.send_message(GROUP_ID, stats, parse_mode="HTML")
                daily_messages.clear()
                daily_new_members = 0
                today = datetime.now().date() + timedelta(days=1)
                await asyncio.sleep(60)
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Ошибка в stats: {e}")
            await asyncio.sleep(60)

# ========== ЗАПУСК ==========
async def main():
    print("🛡 Бот запущен!")
    print("✅ Приветствие с ссылкой на профиль")
    print("✅ /ban, /mute, /warn для админов")
    print("✅ Анти-спам (бан за 3 сообщения за 5 секунд)")
    print("✅ Утро в 05:00, Вечер в 19:00")
    print("✅ Статистика в 19:00")
    print("✅ Периодические сообщения каждые 2 часа")
    
    asyncio.create_task(periodic_messages())
    asyncio.create_task(daily_greetings())
    asyncio.create_task(daily_stats())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
