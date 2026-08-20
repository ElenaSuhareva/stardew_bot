import os
from dotenv import load_dotenv
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY") or os.getenv("YANDEX_API_KEY")  # оставляем как есть
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID") or os.getenv("YANDEX_FOLDER_ID")  # оставляем как есть

if TELEGRAM_TOKEN is None:
    raise ValueError("❌ TELEGRAM_TOKEN не найден! Проверь переменные окружения.")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
waiting_for_question = set()

SEASONS = {
    "Первая весна": "В первый год весной: расчисти участок, посади пастернак и картофель, построй силосную башню, добывай камень и дерево, подружись с жителями, загляни в шахту.",
    "Первое лето": "Летом: сажай чернику и хмель, накопи на разбрызгиватели, улучши инструменты, активно добывай руду, готовься к осени.",
    "Первая осень": "Осень: время тыквы и клюквы, строй теплицы, копай артефакты, развивай отношения, готовься к зиме.",
    "Первая зима": "Зимой: занимайся ремеслом, собирай зимние корни, готовь семена к весне, улучшай ферму, укрепляй дружбу."
}

CHARACTERS = [
    "Эллиот", "Харви", "Сэм", "Шейн", "Алекс", "Пенни",
    "Эмили", "Хэйли", "Лия", "Абигейл", "Мару", "Себастьян"
]

GIFTS = {
    "Эллиот": "Гранат, кроличья лапка, лобстер, тыква, утиное перо",
    "Харви": "Кофе, трюфель, вино, кроличья лапка, радужный осколок",
    "Сэм": "Кленовый пончик, пицца, тигровый глаз, картофель фри, кроличья лапка",
    "Шейн": "Пиво, острый перец, пицца, перец чили, кроличья лапка",
    "Алекс": "Полный завтрак, ужин из лосося, кроличья лапка, золотая тыква",
    "Пенни": "Одуванчик, лук-порей, красная тарелка, дыня, кроличья лапка",
    "Эмили": "Аметист, изумруд, нефрит, рубин, топаз",
    "Хэйли": "Кокос, подсолнух, кроличья лапка, золотая тыква, радужный осколок",
    "Лия": "Салат, жаркое, вино, козий сыр, кроличья лапка",
    "Абигейл": "Аметист, ежевика, острый перец, тыква, кроличья лапка",
    "Мару": "Аккумулятор, медный слиток, железный слиток, кварц, кроличья лапка",
    "Себастьян": "Замороженная слеза, кофе, тыквенный суп, кроличья лапка, радужный осколок"
}

async def get_yandex_response(prompt: str) -> str:
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": "300"
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты помощник по игре Stardew Valley. Отвечай кратко, по делу, без лишней воды. Используй только факты из игры. Если спрашивают про подарки — дай 3–5 любимых подарков персонажа."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            if resp.status != 200:
                return "Сейчас не удаётся получить ответ от ИИ. Попробуй позже."
            data = await resp.json()
            return data["result"]["alternatives"][0]["message"]["text"]

def main_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="🌱 Первый год", callback_data="first_year")
    builder.button(text="🎁 Подарки персонажам", callback_data="gifts_menu")
    builder.button(text="🤖 Задать вопрос", callback_data="ask_question")
    builder.button(text="ℹ️ Помощь", callback_data="help")

    builder.adjust(1, 1, 1, 1)

    return builder.as_markup()

def gifts_keyboard():
    builder = InlineKeyboardBuilder()
    for name in CHARACTERS:
        builder.button(text=name, callback_data=f"gift_{name}")
    builder.button(text="⬅️ Назад", callback_data="back_main")
    builder.adjust(3, 3, 3, 2, 1)
    return builder.as_markup()

def seasons_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="🌱 Первая весна", callback_data="season_spring")
    builder.button(text="☀️ Первое лето", callback_data="season_summer")
    builder.button(text="🍂 Первая осень", callback_data="season_fall")
    builder.button(text="❄️ Первая зима", callback_data="season_winter")
    builder.button(text="⬅️ Назад", callback_data="back_main")

    builder.adjust(1, 1, 1, 1, 1)

    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🌾 Stardew Helper\n\n"
        "Твой помощник по Stardew Valley.\n"
        "Выбери раздел:",
        reply_markup=main_keyboard()
    )

@dp.message(Command("gift"))
async def cmd_gift(message: types.Message):
    await message.answer("Выбери персонажа, чтобы узнать его любимые подарки:", reply_markup=gifts_keyboard())

@dp.callback_query(F.data == "first_year")
async def first_year_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🌱 Первый год\n\nВыбери сезон:",
        reply_markup=seasons_keyboard()
    )
    await callback.answer()

@dp.message(Command("year1"))
async def cmd_year1(message: types.Message):
    await message.answer(
        "🌱 Первый год\n\nВыбери сезон:",
        reply_markup=seasons_keyboard()
    )

@dp.message(Command("ask"))
async def cmd_ask(message: types.Message):
    waiting_for_question.add(message.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="back_main")
    await message.answer(
        "🤖 Задать вопрос\n\n"
        "Напиши любой вопрос по Stardew Valley — я постараюсь помочь.",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🌾 Stardew Helper\n\n"
        "Твой помощник по Stardew Valley.\n"
        "Выбери раздел:",
        reply_markup=main_keyboard()
    )
    await callback.answer()

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "ℹ️ Помощь\n\n"
        "🌱 Первый год — советы по сезонам первого года.\n"
        "🎁 Подарки персонажам — любимые подарки жителей.\n"
        "🤖 Задать вопрос — напиши вопрос по Stardew Valley.\n\n"
        "Также можно использовать меню команд Telegram."
    )

@dp.callback_query(F.data == "help")
async def help_button(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ Помощь\n\n"
        "🌱 Первый год — советы по сезонам первого года.\n"
        "🎁 Подарки персонажам — любимые подарки жителей.\n"
        "🤖 Задать вопрос — вопрос по Stardew Valley через ИИ.\n\n"
        "Также можно использовать меню команд Telegram.",
        reply_markup=main_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("season_"))
async def handle_season(callback: types.CallbackQuery):
    season_key = callback.data.replace("season_", "")
    reverse_map = {
        "spring": "Первая весна",
        "summer": "Первое лето",
        "fall": "Первая осень",
        "winter": "Первая зима"
    }
    text = SEASONS[reverse_map[season_key]]
    await callback.message.edit_text(
        text,
        reply_markup=seasons_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "gifts_menu")
async def gifts_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🎁 Подарки персонажам\n\nВыбери персонажа:",
        reply_markup=gifts_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("gift_"))
async def handle_gift(callback: types.CallbackQuery):
    character = callback.data.replace("gift_", "")
    gifts = GIFTS.get(character, "Не удалось найти список подарков.")
    await callback.message.edit_text(
        f"Любимые подарки для {character}:\n{gifts}",
        reply_markup=gifts_keyboard()
    )

@dp.callback_query(F.data == "ask_question")
async def ask_question_placeholder(callback: types.CallbackQuery):
    waiting_for_question.add(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="back_main")
    await callback.message.edit_text(
        "🤖 Задать вопрос\n\n"
        "Напиши любой вопрос по Stardew Valley — я постараюсь помочь.",
        reply_markup=builder.as_markup()
    )
    await callback.answer()

@dp.message()
async def handle_text_question(message: types.Message):
    user_id = message.from_user.id
    if user_id not in waiting_for_question:
        return
    waiting_for_question.remove(user_id)
    prompt = f"Ответь кратко и по делу на вопрос по Stardew Valley: {message.text}"
    try:
        response = await get_yandex_response(prompt)
        await message.reply(response)
    except Exception:
        await message.reply(
            "Сейчас не удаётся получить ответ от ИИ. Попробуй позже."
        )

async def main():
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Главное меню"),
        types.BotCommand(command="year1", description="Первый год"),
        types.BotCommand(command="gift", description="Подарки персонажам"),
        types.BotCommand(command="ask", description="Задать вопрос"),
        types.BotCommand(command="help", description="Помощь"),
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

