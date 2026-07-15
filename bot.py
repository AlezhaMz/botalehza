import asyncio
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8762058651:AAGTU6a3ktSWK03lszxZa4iPc7-bawGK3Ek"  # ЗАМЕНИ НА НОВЫЙ ТОКЕН!
GROUP_ID = -1003666056371
ADMIN_IDS = [1487417026]
# =================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== ДАННЫЕ ==========
daily_messages = defaultdict(int)
daily_new_members = 0
today = datetime.now().date()

# ========== УДАЛЕНИЕ СИСТЕМНЫХ СООБЩЕНИЙ ==========
@dp.message(F.content_type.in_([
    types.ContentType.NEW_CHAT_MEMBERS,
    types.ContentType.LEFT_CHAT_MEMBER
]))
async def delete_service_messages(message: types.Message):
    """Удаляет сообщения о входе/выходе"""
    try:
        await message.delete()
        print(f"🗑 Удалено: {message.content_type}")
    except:
        pass

# ========== ПРИВЕТСТВИЕ ==========
@dp.message(F.content_type == types.ContentType.NEW_CHAT_MEMBERS)
async def welcome_user(message: types.Message):
    global daily_new_members, today
    
    # Проверка смены дня
    now = datetime.now().date()
    if now != today:
        today = now
        daily_new_members = 0
        daily_messages.clear()
    
    for user in message.new_chat_members:
        if user.id == bot.id:
            continue
        
        # Проверка на ботов
        if user.is_bot:
            try:
                await bot.ban_chat_member(GROUP_ID, user.id)
                await message.answer(f"🚫 Бот {user.full_name} удалён!")
            except:
                pass
            continue
        
        daily_new_members += 1
        
        # Приветствие
        greeting = (
            f"👋 Приветствуем {user.full_name}, в Лавке главного торговца!\n\n"
            f"• <a href='https://t.me/ShopkeepersCache/17163'>Узнать о нас</a>\n"
            f"• <a href='https://t.me/ShopkeepersCache'>Ассортимент</a>\n"
            f"• <a href='https://t.me/StashShopkeepers'>Наш канал</a>"
        )
        try:
            await message.answer(greeting, parse_mode="HTML", disable_web_page_preview=True)
        except:
            pass

# ========== СТАТИСТИКА СООБЩЕНИЙ ==========
@dp.message(F.text)
async def count_messages(message: types.Message):
    if message.chat.id != GROUP_ID:
        return
    
    if message.from_user.is_bot:
        return
    
    if message.from_user.id in ADMIN_IDS:
        return
    
    daily_messages[message.from_user.id] += 1

# ========== ПЕРИОДИЧЕСКИЕ СООБЩЕНИЯ ==========
MESSAGES = [
    "➤ Ищете компанию для Dota 2? Присоединяйтесь к нашему <a href='https://discord.gg/AtQypC6jK'>Discord-серверу</a>",
    "➤ Скидки и новости в Telegram-канале <a href='https://t.me/StashShopkeepers'>«Тайны Торговца»</a>",
    "➤ Общайтесь, торгуйте, находите друзей по Dota 2 в нашем чате!"
]

async def periodic_messages():
    index = 0
    last_msg_id = None
    
    while True:
        try:
            now = datetime.now()
            
            # Работаем с 9:00 до 23:00
            if 9 <= now.hour < 23:
                # Удаляем предыдущее сообщение
                if last_msg_id:
                    try:
                        await bot.delete_message(GROUP_ID, last_msg_id)
                    except:
                        pass
                
                # Отправляем новое
                msg = await bot.send_message(
                    GROUP_ID,
                    MESSAGES[index % len(MESSAGES)],
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                last_msg_id = msg.message_id
                index += 1
                
                await asyncio.sleep(7200)  # 2 часа
            else:
                await asyncio.sleep(60)  # Ночью проверяем каждую минуту
                
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(60)

# ========== УТРО И ВЕЧЕР ==========
async def daily_greetings():
    last_greeting = None
    last_farewell = None
    
    while True:
        try:
            now = datetime.now()
            
            # Утро 9:00
            if now.hour == 9 and now.minute == 0 and last_greeting != now.date():
                await bot.send_message(
                    GROUP_ID,
                    "☀️ <b>Доброе утро!</b>\n\n"
                    "Лавка открыта!\n"
                    "Хороших покупок и приятной игры! 🎮",
                    parse_mode="HTML"
                )
                last_greeting = now.date()
                await asyncio.sleep(60)
            
            # Вечер 23:00
            if now.hour == 23 and now.minute == 0 and last_farewell != now.date():
                await bot.send_message(
                    GROUP_ID,
                    "🌙 <b>Лавка закрывается!</b>\n\n"
                    "Спокойной ночи!\n"
                    "До встречи завтра! 😴",
                    parse_mode="HTML"
                )
                last_farewell = now.date()
                await asyncio.sleep(60)
            
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(60)

# ========== СТАТИСТИКА ==========
async def daily_stats():
    global daily_messages, daily_new_members, today
    
    while True:
        try:
            now = datetime.now()
            
            if now.hour == 23 and now.minute == 0:
                try:
                    members = await bot.get_chat_member_count(GROUP_ID)
                except:
                    members = 0
                
                # Находим самого активного
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
                    "📊 <b>Статистика за сегодня</b>\n\n"
                    f"👥 Участников: {members}\n"
                    f"💬 Сообщений: {sum(daily_messages.values())}\n"
                    f"🆕 Новых: {daily_new_members}\n"
                    f"🏆 Самый активный: {top_user} ({top_count} сообщений)\n"
                    f"📅 {now.strftime('%d.%m.%Y')}"
                )
                
                await bot.send_message(GROUP_ID, stats, parse_mode="HTML")
                
                # Очищаем данные
                daily_messages.clear()
                daily_new_members = 0
                today = datetime.now().date() + timedelta(days=1)
                
                await asyncio.sleep(60)
            
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(60)

# ========== ЗАПУСК ==========
async def main():
    print("🛡 Бот запущен!")
    print("✅ Удаление системных сообщений")
    print("✅ Приветствие новых участников")
    print("✅ Периодические сообщения (каждые 2 часа)")
    print("✅ Утреннее/вечернее приветствие")
    print("✅ Статистика в 23:00")
    
    # Запускаем фоновые задачи
    asyncio.create_task(periodic_messages())
    asyncio.create_task(daily_greetings())
    asyncio.create_task(daily_stats())
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
