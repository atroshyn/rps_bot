# (Повний код такий самий, як у попередньому кроці — вставляємо сюди знову)
# Щоб уникнути дублювання тут, ми збережемо код як файл.

# === АДМІН КОМАНДИ ===

ADMIN_IDS = [123456789]  # заміни на свій Telegram ID

def is_admin(user_id):
    return user_id in ADMIN_IDS

@dp.message_handler(commands=['allusers'])
async def all_users(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ заборонено.")
        return
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, games, wins, losses, draws FROM users ORDER BY games DESC")
    users = cur.fetchall()
    conn.close()
    if not users:
        await message.answer("Немає зареєстрованих гравців.")
        return
    response = "Список усіх гравців:

"
    for user in users:
        uid, games, wins, losses, draws = user
        response += f"ID {uid} — Ігор: {games}, В:{wins} П:{losses} Н:{draws}
"
    await message.answer(response[:4096])  # Telegram обмеження

@dp.message_handler(commands=['cleardata'])
async def clear_all_data(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ заборонено.")
        return
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users")
    cur.execute("DELETE FROM games")
    conn.commit()
    conn.close()
    await message.answer("Усі дані очищено.")