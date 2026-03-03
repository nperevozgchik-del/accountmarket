import asyncio
import json
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = "8662565700:AAFLifAwGVmObgee25DlAbmfNOgtIWMC5jI"  # Получи у @BotFather
WEB_APP_URL = "https://nperevozgchik-del.github.io/accountmarket/"  # Ссылка на GitHub Pages
YOUR_TELEGRAM_ID = 2035626077  # Твой ID (узнай у @userinfobot)
# ===============================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Функция для форматирования данных
def format_form_data(data):
    """Красиво форматирует данные из формы"""
    user_data = data.get('data', {})
    user_info = data.get('user', {})
    
    # Эмодзи для приоритета
    priority_emojis = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🔴'
    }
    
    priority = user_data.get('priority', 'low')
    priority_emoji = priority_emojis.get(priority, '⚪')
    
    # Формируем сообщение
    text = f"""
📨 <b>НОВАЯ ЗАЯВКА</b>
━━━━━━━━━━━━━━━
⏰ <b>Время:</b> {data.get('timestamp', datetime.now().isoformat())}

👤 <b>Информация о пользователе:</b>
├ ID: <code>{user_info.get('id', 'Неизвестно')}</code>
├ Имя: {user_info.get('first_name', 'Неизвестно')} {user_info.get('last_name', '')}
├ Username: @{user_info.get('username', 'Нет')}
└ Язык: {user_info.get('language_code', 'Неизвестно')}

📋 <b>Данные формы:</b>
├ 👤 Имя: <code>{user_data.get('name', 'Не указано')}</code>
├ 📧 Email: <code>{user_data.get('email', 'Не указано')}</code>
├ 📱 Телефон: <code>{user_data.get('phone', 'Не указан')}</code>
├ 📌 Тема: <code>{user_data.get('subject', 'Не указана')}</code>
├ {priority_emoji} Приоритет: <code>{user_data.get('priority', 'Не указан').upper()}</code>
└ 📎 Файл: <code>{user_data.get('has_file', 'Нет')}</code>

💬 <b>Сообщение:</b>
━━━━━━━━━━━━━━━
{user_data.get('message', 'Пусто')}
━━━━━━━━━━━━━━━
    """
    return text

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Заполнить форму",
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ О боте",
                    callback_data="info"
                ),
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="stats"
                )
            ]
        ]
    )
    
    welcome_text = """
👋 <b>Привет! Я бот для сбора обратной связи.</b>

Что я умею:
• 📝 Собирать данные через красивую форму
• 📎 Принимать файлы
• 📊 Сортировать по приоритетам
• ⚡ Мгновенно отправлять тебе уведомления

👇 <b>Нажми кнопку ниже, чтобы начать</b>
    """
    
    await message.answer(
        welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# Обработка данных из мини-приложения
@dp.message(lambda message: message.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        # Получаем данные
        data = json.loads(message.web_app_data.data)
        
        if data.get('type') == 'form_submission':
            # Форматируем данные
            formatted_text = format_form_data(data)
            
            # Отправляем тебе в личку
            await bot.send_message(
                chat_id=YOUR_TELEGRAM_ID,
                text=formatted_text,
                parse_mode="HTML"
            )
            
            # Отправляем подтверждение пользователю
            await message.answer(
                "✅ <b>Спасибо!</b>\n\n"
                "Твоя заявка успешно отправлена создателю.\n"
                "Обычно ответ приходит в течение 24 часов.\n\n"
                "Хочешь отправить ещё? Нажми /start",
                parse_mode="HTML"
            )
            
            # Логирование
            logging.info(f"Получена заявка от {message.from_user.id}")
            
    except Exception as e:
        logging.error(f"Ошибка при обработке: {e}")
        await message.answer(
            "❌ <b>Ошибка</b>\n\n"
            "Что-то пошло не так. Попробуй ещё раз позже.",
            parse_mode="HTML"
        )

# Обработка кнопок
@dp.callback_query(lambda c: c.data == "info")
async def process_callback_info(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    
    info_text = """
ℹ️ <b>О боте</b>

Этот бот создан для сбора обратной связи.
Все данные отправляются напрямую создателю.

<b>Версия:</b> 1.0
<b>Разработчик:</b> @username
    """
    
    await bot.send_message(
        callback_query.from_user.id,
        info_text,
        parse_mode="HTML"
    )

@dp.callback_query(lambda c: c.data == "stats")
async def process_callback_stats(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(
        callback_query.id,
        text="📊 Статистика пока не доступна",
        show_alert=False
    )

# Запуск бота
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    print("🤖 Бот запущен и готов к работе!")
    print(f"📱 Ссылка на приложение: {WEB_APP_URL}")
    print(f"👤 Твой ID: {YOUR_TELEGRAM_ID}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
