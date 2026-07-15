import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberUpdated

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8762058651:AAGTU6a3ktSWK03lszxZa4iPc7-bawGK3Ek"  # ВАШ ТОКЕН
GROUP_ID = -1003666056371
ADMIN_IDS = [1487417026]

# ========== ID ТЕМ ==========
REVIEWS_TOPIC_ID = 262
TRADE_TOPIC_ID = 3869

# ========== НАСТРОЙКИ ДЛЯ TRADE ЧАТ ==========
ALLOWED_TAGS = ["#продам", "#куплю", "#обменяю"]
RULES_URL = "https://t.me/ShopkeepersCache/3869/3870"

# =====================================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== ДАННЫЕ ДЛЯ СТАТИСТИКИ ==========
STATS_FILE = "stats.json"
daily_messages = defaultdict(int)
daily_new_members = 0
daily_left_members = 0
today = datetime.now().date()

def load_stats():
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except:
        pass
    return {}

def save_stats(data):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

# ========== ПРИВЕТСТВИЕ НОВЫХ УЧАСТНИКОВ ==========
@dp.chat_member()
async def welcome_new_member(event: ChatMemberUpdated):
    if event.chat.id != GROUP_ID:
        return
    if event.new_chat_member.user.id == bot.id:
        return
    if event.new_chat_member.status not in ["member", "administrator"]:
        return
    
    global daily_new_members, today
    now = datetime.now().date()
    if now != today:
        today = now
        daily_new_members = 0
        daily_left_members = 0
        daily_messages.clear()
    
    daily_new_members += 1
    
    user = event.new_chat_member.user
    greeting = (
        f"👋 Приветствуем {user.full_name}, в Лавке главного торговца!\n"
        f"Можешь пообщаться с нами в чате или:\n"
        f"• <a href='https://t.me/ShopkeepersCache/17163'>Узнать о нас подробнее</a>\n"
        f"• <a href='https://t.me/ShopkeepersCache'>Ознакомиться с ассортиментом</a>\n"
        f"• <a href='https://t.me/StashShopkeepers'>Посетить канал лавки</a>"
    )
    await bot.send_message(
        chat_id=GROUP_ID,
        text=greeting,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

# ========== УДАЛЕНИЕ СООБЩЕНИЙ О ВЫХОДЕ ==========
@dp.message()
async def goodbye_clean(message: types.Message):
    if message.chat.id != GROUP_ID:
        return
    if message.left_chat_member:
        try:
            await message.delete()
        except:
            pass

# ========== АВТООТВЕТ В ТЕМЕ "ОТЗЫВЫ" ==========
@dp.message()
async def handle_reviews(message: types.Message):
    if message.chat.id != GROUP_ID:
        return
    if message.message_thread_id != REVIEWS_TOPIC_ID:
        return
    if message.from_user.id == bot.id:
        return
    if message.text and message.text.startswith('/'):
        return

    await bot.send_message(
        chat_id=GROUP_ID,
        text=(
            "Спасибо, что нашли время оставить отзыв! 🙏\n\n"
            "Для нас действительно важно каждое мнение и мы доказываем это делом. "
            "Мы выбрали максимально открытую систему публикации: ваши слова увидят все, "
            "без предварительной фильтрации.\n\n"
            "Мы знаем: доверие строится на честности. Поэтому мы готовы к похвале, "
            "конструктивной критике и даже жёсткому несогласию — это помогает нам расти."
        ),
        message_thread_id=REVIEWS_TOPIC_ID
    )

# ========== МОДЕРАЦИЯ ТЕМЫ "TRADE ЧАТ" ==========
@dp.message()
async def trade_chat_moderation(message: types.Message):
    if message.chat.id != GROUP_ID:
        return
    if message.message_thread_id != TRADE_TOPIC_ID:
        return
    if message.from_user.id == bot.id:
        return
    if message.from_user.id in ADMIN_IDS:
        return
    
    has_allowed_tag = any(tag in message.text.lower() for tag in ALLOWED_TAGS)
    
    if not has_allowed_tag:
        try:
            await message.delete()
        except:
            pass
        
        warning = await bot.send_message(
            chat_id=GROUP_ID,
            text=(
                f"⚠️ {message.from_user.first_name}, в теме **Trade чат** разрешены только сообщения с тегами:\n"
                f"`#продам`  `#куплю`  `#обменяю`\n\n"
                f"Пример: `#продам Аркану на Pudge`"
            ),
            message_thread_id=TRADE_TOPIC_ID,
            parse_mode="Markdown"
        )
        
        await asyncio.sleep(5)
        try:
            await warning.delete()
        except:
            pass

# ========== АВТООТВЕТ В ТЕМЕ "TRADE ЧАТ" С ПРАВИЛАМИ ==========
@dp.message()
async def trade_chat_reminder(message: types.Message):
    if message.chat.id != GROUP_ID:
        return
    if message.message_thread_id != TRADE_TOPIC_ID:
        return
    if message.from_user.id == bot.id:
        return
    if message.text and message.text.startswith('/'):
        return
    
    current_time = datetime.now()
    if hasattr(trade_chat_reminder, 'last_reply_time'):
        time_diff = (current_time - trade_chat_reminder.last_reply_time).seconds
        if time_diff < 300:
            return
    trade_chat_reminder.last_reply_time = current_time
    
    await bot.send_message(
        chat_id=GROUP_ID,
        text=(
            f"💬 В этом разделе можно обмениваться вещами между собой. Пожалуйста, не забывайте о главном — соблюдайте наши <a href='{RULES_URL}'>правила</a>!"
        ),
        message_thread_id=TRADE_TOPIC_ID,
        parse_mode="HTML",
        disable_web_page_preview=False
    )

# ========== ЗАЩИТА ОТ СПАМА ==========
user_last_msg = {}
user_warns = {}

@dp.message()
async def anti_spam(message: types.Message):
    if message.chat.id != GROUP_ID:
        return
    if message.text and message.text.startswith('/'):
        return
    
    if message.message_thread_id in [REVIEWS_TOPIC_ID, TRADE_TOPIC_ID]:
        return
    
    global daily_messages, today
    
    now = datetime.now().date()
    if now != today:
        today = now
        daily_new_members = 0
        daily_left_members = 0
        daily_messages.clear()
    
    if message.from_user.id in ADMIN_IDS or message.from_user.is_bot:
        return
    
    user_id = message.from_user.id
    daily_messages[user_id] += 1
    
    if user_id in user_last_msg:
        time_diff = (datetime.now() - user_last_msg[user_id]).seconds
        if time_diff < 5:
            user_warns[user_id] = user_warns.get(user_id, 0) + 1
            if user_warns[user_id] >= 3:
                await bot.ban_chat_member(GROUP_ID, user_id)
                await message.answer(f"🚫 {message.from_user.full_name} забанен за спам!")
                del user_last_msg[user_id]
                del user_warns[user_id]
                return
        else:
            user_warns[user_id] = 0
    user_last_msg[user_id] = datetime.now()

# ========== КОМАНДЫ АДМИНОВ ==========
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
        await message.answer("❌ Нельзя замутить администратора или создателя!")
        return
    until_date = datetime.now() + timedelta(minutes=5)
    try:
        await bot.restrict_chat_member(
            GROUP_ID, user_id, until_date=until_date,
            can_send_messages=False, can_send_media_messages=False,
            can_send_other_messages=False, can_add_web_page_previews=False
        )
        await message.answer(f"🔇 {message.reply_to_message.from_user.first_name} замучен на 5 минут!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)[:100]}")

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
        await message.answer("❌ Нельзя забанить администратора или создателя!")
        return
    try:
        await bot.ban_chat_member(GROUP_ID, user_id)
        await message.answer(f"🚫 {message.reply_to_message.from_user.first_name} забанен!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)[:100]}")

# ========== КОМАНДА ДЛЯ УЗНАВАНИЯ ID ТЕМЫ ==========
@dp.message(Command('topic_id'))
async def show_topic_id(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        topic_id = message.message_thread_id
        if topic_id:
            await message.answer(
                f"🆔 ID этой темы: `{topic_id}`\n\nИспользуй этот ID в коде.",
                parse_mode="Markdown"
            )
        else:
            await message.answer("❌ Эта команда работает только в темах!")

# ========== ПЕРИОДИЧЕСКИЕ СООБЩЕНИЯ ==========
CONFIG_FILE = "config.json"

def load_config():
    default = {
        "periodic_messages": [],
        "current_index": 0,
        "last_message_id": None
    }
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    return data
    except:
        pass
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(default, f, ensure_ascii=False, indent=2)
    return default

def save_config(data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

async def periodic_messages():
    while True:
        try:
            now = datetime.now()
            if now.hour >= 23 or now.hour < 9:
                await asyncio.sleep(60)
                continue
            
            config = load_config()
            messages = config.get("periodic_messages", [])
            if messages:
                if config.get("last_message_id"):
                    try:
                        await bot.delete_message(GROUP_ID, config["last_message_id"])
                    except:
                        pass
                idx = config.get("current_index", 0) % len(messages)
                msg = messages[idx]
                sent = await bot.send_message(GROUP_ID, msg, parse_mode="HTML", disable_web_page_preview=False)
                config["current_index"] = idx + 1
                config["last_message_id"] = sent.message_id
                save_config(config)
            await asyncio.sleep(7200)
        except Exception as e:
            print(f"Ошибка в периодических сообщениях: {e}")
            await asyncio.sleep(60)

# ========== СТАТИСТИКА ГРУППЫ ==========
async def send_daily_stats():
    global daily_messages, daily_new_members, daily_left_members, today
    while True:
        try:
            now = datetime.now()
            if now.hour == 23 and now.minute == 0:
                try:
                    member_count = await bot.get_chat_member_count(GROUP_ID)
                except:
                    member_count = 0
                if daily_messages:
                    top_user_id = max(daily_messages, key=daily_messages.get)
                    top_count = daily_messages[top_user_id]
                    try:
                        top_user = await bot.get_chat(top_user_id)
                        top_name = top_user.first_name or "Неизвестный"
                    except:
                        top_name = "Неизвестный"
                else:
                    top_name = "Нет сообщений"
                    top_count = 0
                stats_text = (
                    "📊 <b>Статистика группы за сегодня</b>\n\n"
                    f"👥 Всего участников: {member_count}\n"
                    f"💬 Сообщений: {sum(daily_messages.values())}\n"
                    f"🆕 Новых участников: {daily_new_members}\n"
                    f"📅 {now.strftime('%d.%m.%Y')}"
                )
                await bot.send_message(GROUP_ID, stats_text, parse_mode="HTML")
                await asyncio.sleep(10)
                daily_messages.clear()
                daily_new_members = 0
                daily_left_members = 0
                today = datetime.now().date() + timedelta(days=1)
                await asyncio.sleep(60)
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Ошибка в статистике: {e}")
            await asyncio.sleep(60)

# ========== УТРЕННИЕ И ВЕЧЕРНИЕ ==========
async def daily_greetings():
    last_greeting = None
    last_farewell = None
    while True:
        try:
            now_utc = datetime.now(timezone.utc)
            now_msk = now_utc + timedelta(hours=3)
            now_time = now_msk.time()
            now_date = now_msk.date()
            
            if now_time.hour == 9 and now_time.minute == 0 and last_greeting != now_date:
                await bot.send_message(
                    GROUP_ID,
                    "☀️ <b>Доброе утро, Лавка Торговца!</b>\n\n"
                    "Начинаем новый день в мире Dota 2!\n"
                    "➤ Свежие сеты уже на полках.\n"
                    "➤ Будьте вежливы и соблюдайте правила чата.\n"
                    "➤ Хороших покупок и приятной игры! 🎮",
                    parse_mode="HTML"
                )
                last_greeting = now_date
                await asyncio.sleep(60)
            
            if now_time.hour == 23 and now_time.minute == 0 and last_farewell != now_date:
                await bot.send_message(
                    GROUP_ID,
                    "🌙 <b>Лавка закрывается!</b>\n\n"
                    "Всем спать! Завтра будет новый день.\n"
                    "➤ Не шалите без меня! 😴\n"
                    "➤ Завтра я открою для тебя новые тайны.\n"
                    "➤ До встречи на рассвете! 🗡️",
                    parse_mode="HTML"
                )
                last_farewell = now_date
                await asyncio.sleep(60)
            
            await asyncio.sleep(30)
        except Exception as e:
            print(f"Ошибка в ежедневных приветствиях: {e}")
            await asyncio.sleep(60)

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("🛡 Лавка Торговца — бот запущен!")
    print("✅ Автоответ в теме 'Отзывы'")
    print("✅ Модерация в теме 'Trade чат' (только с тегами)")
    print("✅ Автоответ с правилами в теме 'Trade чат'")
    print("✅ Приветствие новых участников")
    print("✅ Защита от спама (с исключением для тем)")
    print("✅ Периодические сообщения (каждые 2 часа)")
    print("✅ Утренние и вечерние сообщения (по Москве)")
    print("✅ Статистика группы")
    print("✅ Админ-команды: /mute, /ban, /topic_id")

    async def main():
        loop = asyncio.get_event_loop()
        loop.create_task(periodic_messages())
        loop.create_task(daily_greetings())
        loop.create_task(send_daily_stats())
        
        await dp.start_polling(bot, skip_updates=True)
    
    asyncio.run(main())
