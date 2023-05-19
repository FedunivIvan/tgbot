import telebot
from telebot import types

# Создание экземпляра бота
bot = telebot.TeleBot('5761676599:AAHjLEChmM_3dkylEM3xJsfJG88dAMCra40')

# Хранилище рецензий пользователя
reviews = []

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = get_menu_keyboard()
    bot.send_message(message.chat.id, "Добро пожаловать в Книжного рецензента! Выберите действие:", reply_markup=markup)

# Получение клавиатуры главного меню
def get_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Мои рецензии", callback_data="my_reviews:0"))
    keyboard.add(types.InlineKeyboardButton(text="Новая рецензия", callback_data="add_review_title"))
    return keyboard

# Обработчик нажатия кнопок
@bot.callback_query_handler(func=lambda call: True)
def button_handler(call):
    if call.data.startswith("my_reviews"):
        page = int(call.data.split(":")[1])
        my_reviews(call.message.chat.id, page)
    elif call.data == "add_review_title":
        add_review_title(call.message.chat.id)
    elif call.data.startswith("delete_review"):
        delete_review(call.message.chat.id, call.data.split(":")[1])
    elif call.data.startswith("skip_review"):
        skip_review_step(call.message.chat.id, call.data.split(":")[1])

# Обработчик команды "Мои рецензии"
def my_reviews(chat_id, page):
    num_reviews = len(reviews)
    start_index = page * 4
    end_index = min(start_index + 4, num_reviews)
    
    if num_reviews == 0:
        bot.send_message(chat_id, "У вас пока нет рецензий.")
        return
    
    for index in range(start_index, end_index):
        review = reviews[index]
        markup = get_review_keyboard(index)
        bot.send_message(chat_id, format_review(review), reply_markup=markup)
    
    if end_index < num_reviews:
        markup = get_next_page_keyboard(page + 1)
        bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

# Получение клавиатуры для рецензии
def get_review_keyboard(review_index):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Удалить", callback_data=f"delete_review:{review_index}"))
    return keyboard

# Получение клавиатуры для перехода к следующей странице рецензий
def get_next_page_keyboard(page):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Далее", callback_data=f"my_reviews:{page}"))
    return keyboard

# Обработчик команды "Новая рецензия"
def add_review_title(chat_id):
    msg = bot.send_message(chat_id, "Введите название книги:")
    bot.register_next_step_handler(msg, add_review_author)

# Обработчик ввода названия книги
def add_review_author(message):
    review = {'title': message.text}
    reviews.append(review)
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Введите автора книги:")
    bot.register_next_step_handler(msg, add_review_comment)

# Обработчик ввода автора книги
def add_review_comment(message):
    review = reviews[-1]
    review['author'] = message.text
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Введите комментарий к книге:")
    bot.register_next_step_handler(msg, add_review_rating)

# Обработчик ввода комментария к книге
def add_review_rating(message):
    review = reviews[-1]
    review['comment'] = message.text
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Введите оценку от 1 до 10 (или пропустите это поле):")
    bot.register_next_step_handler(msg, validate_review_rating)

# Проверка валидности оценки книги
def validate_review_rating(message):
    review = reviews[-1]
    rating = message.text.strip()
    
    if rating.isdigit() and 1 <= int(rating) <= 10:
        review['rating'] = int(rating)
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Введите цитату из книги (или пропустите это поле):")
        bot.register_next_step_handler(msg, finish_adding_review)
    else:
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Некорректная оценка. Пожалуйста, введите оценку от 1 до 10:")
        bot.register_next_step_handler(msg, validate_review_rating)

# Завершение добавления рецензии
def finish_adding_review(message):
    review = reviews[-1]
    review['quote'] = message.text
    chat_id = message.chat.id
    bot.send_message(chat_id, "Рецензия успешно добавлена!")
    markup = get_menu_keyboard()
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

# Удаление рецензии
def delete_review(chat_id, review_index):
    index = int(review_index)
    if index >= 0 and index < len(reviews):
        del reviews[index]
        bot.send_message(chat_id, "Рецензия успешно удалена.")
    else:
        bot.send_message(chat_id, "Некорректный номер рецензии.")

# Форматирование рецензии
def format_review(review):
    title = f"📖 Название: {review['title']}"
    author = f"👤 Автор: {review['author']}"
    comment = f"💬 Комментарий: {review['comment']}"
    
    rating = review.get('rating')
    rating_text = f"⭐ Оценка: {rating}" if rating else "⭐ Оценка: не указана"
    
    quote = review.get('quote')
    quote_text = f"🔖 Цитата: {quote}" if quote else "🔖 Цитата: не указана"
    
    return f"{title}\n{author}\n{comment}\n{rating_text}\n{quote_text}"

# Пропуск шага добавления рецензии
def skip_review_step(chat_id, step):
    if step == "rating":
        review = reviews[-1]
        review['rating'] = None
        chat_id = message.chat.id
        msg = bot.send_message(chat_id, "Введите цитату из книги (или пропустите это поле):")
        bot.register_next_step_handler(msg, finish_adding_review)
    elif step == "quote":
        review = reviews[-1]
        review['quote'] = None
        chat_id = message.chat.id
        bot.send_message(chat_id, "Рецензия успешно добавлена!")
        markup = get_menu_keyboard()
        bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

# Запуск бота
bot.polling()
