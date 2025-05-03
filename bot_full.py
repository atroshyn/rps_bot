
# Gjdyf № Повна версія без БД


import random
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

API_TOKEN = 'YOUR_BOT_TOKEN'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

games = {}       # PvP ігри
user_stats = {}  # Статистика гравців

# Емодзі для відображення ходу
def emoji(move):
    return {"rock": "✊", "scissors": "✌️", "paper": "✋"}.get(move, "")

# Визначення переможця
def determine_winner(p1, p2):
    beats = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
    if p1 == p2:
        return "Нічия!"
    elif beats[p1] == p2:
        return "Ти переміг!"
    else:
        return "Твій суперник переміг!"

# Оновлення статистики
def update_stats(winner_id, loser_id=None, draw=False):
    for uid in [winner_id, loser_id]:
        if uid and uid not in user_stats:
            user_stats[uid] = {"wins": 0, "losses": 0, "draws": 0, "games": 0}

    if draw:
        for uid in [winner_id, loser_id]:
            if uid:
                user_stats[uid]["draws"] += 1
                user_stats[uid]["games"] += 1
    else:
        user_stats[winner_id]["wins"] += 1
        user_stats[winner_id]["games"] += 1
        if loser_id:
            user_stats[loser_id]["losses"] += 1
            user_stats[loser_id]["games"] += 1

# Старт / посилання на виклик
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    args = message.get_args()
    if args.startswith("challenge_"):
        game_id = args.replace("challenge_", "")
        game = games.get(game_id)
        if not game or game["player2_id"]:
            await message.answer("Цей виклик уже використано або недійсний.")
            return

        keyboard = InlineKeyboardMarkup()
        for move in ['Камінь ✊', 'Ножиці ✌️', 'Папір ✋']:
            keyboard.add(InlineKeyboardButton(move, callback_data=f"accept_{game_id}_{move.split()[0].lower()}"))
        await message.answer("Тебе викликали на гру! Обери свій хід:", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("Грати з ботом", callback_data='play_bot'),
            InlineKeyboardButton("Кинути виклик другу", callback_data='challenge_friend')
        )
        await message.answer("Привіт! Обери режим гри:", reply_markup=keyboard)

# Команда /stats
@dp.message_handler(commands=['stats'])
async def stats(message: types.Message):
    stats = user_stats.get(message.from_user.id)
    if not stats:
        await message.answer("Ти ще не грав жодної гри.")
        return

    await message.answer(
        f"Твоя статистика:\n"
        f"- Ігор зіграно: {stats['games']}\n"
        f"- Перемог: {stats['wins']}\n"
        f"- Поразок: {stats['losses']}\n"
        f"- Нічиїх: {stats['draws']}"
    )

# Гра з ботом
@dp.callback_query_handler(lambda c: c.data == 'play_bot')
async def play_bot(call: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    for move in ['Камінь ✊', 'Ножиці ✌️', 'Папір ✋']:
        keyboard.add(InlineKeyboardButton(move, callback_data=f"bot_move_{move.split()[0].lower()}"))
    await call.message.edit_text("Обери свій хід:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("bot_move_"))
async def bot_game(call: types.CallbackQuery):
    player_move = call.data.replace("bot_move_", "")
    bot_move = random.choice(["rock", "paper", "scissors"])
    result = determine_winner(player_move, bot_move)

    msg = f"Ти: {emoji(player_move)}\nБот: {emoji(bot_move)}\n\n{result}"
    await call.message.edit_text(msg)

    if result == "Ти переміг!":
        update_stats(call.from_user.id)
    elif result == "Твій суперник переміг!":
        update_stats("bot", call.from_user.id)
    else:
        update_stats(call.from_user.id, "bot", draw=True)

# Кинути виклик другу
@dp.callback_query_handler(lambda c: c.data == 'challenge_friend')
async def challenge_friend(call: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    for move in ['Камінь ✊', 'Ножиці ✌️', 'Папір ✋']:
        keyboard.add(InlineKeyboardButton(move, callback_data=f"pvp_move_{move.split()[0].lower()}"))
    await call.message.edit_text("Обери свій хід для виклику:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("pvp_move_"))
async def set_pvp_move(call: types.CallbackQuery):
    move = call.data.replace("pvp_move_", "")
    game_id = str(uuid.uuid4())[:8]
    games[game_id] = {
        "player1_id": call.from_user.id,
        "player1_move": move,
        "player2_id": None,
        "player2_move": None
    }
    link = f"https://t.me/YOUR_BOT_USERNAME?start=challenge_{game_id}"
    await call.message.edit_text(
        f"Твій хід збережено!\n\nСкопіюй це посилання та надішли другові, щоб прийняти виклик:\n{link}"
    )

# Прийняти виклик
@dp.callback_query_handler(lambda c: c.data.startswith("accept_"))
async def accept_challenge(call: types.CallbackQuery):
    _, game_id, move = call.data.split("_")
    game = games.get(game_id)
    if not game or game["player2_id"]:
        await call.message.edit_text("Цей виклик уже недійсний.")
        return

    game["player2_id"] = call.from_user.id
    game["player2_move"] = move

    p1 = game["player1_move"]
    p2 = move
    result = determine_winner(p1, p2)

    # Повідомлення обом
    await bot.send_message(game["player1_id"],
        f"Суперник зробив хід!\n\nТи: {emoji(p1)}\nДруг: {emoji(p2)}\n\n{result}"
    )
    await call.message.edit_text(
        f"Гру завершено!\n\nТи: {emoji(p2)}\nСуперник: {emoji(p1)}\n\n{result}"
    )

    # Статистика
    if result == "Ти переміг!":
        update_stats(call.from_user.id, game["player1_id"])
    elif result == "Твій суперник переміг!":
        update_stats(game["player1_id"], call.from_user.id)
    else:
        update_stats(game["player1_id"], call.from_user.id, draw=True)

if __name__ == '__main__':
    executor.start_polling(dp)
