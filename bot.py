import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import telebot
from telebot import types


BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID_RAW = os.environ.get("ADMIN_CHAT_ID")

if not BOT_TOKEN:
    raise RuntimeError("Environment variable BOT_TOKEN is required")

ADMIN_CHAT_ID: Optional[int]
try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_RAW) if ADMIN_CHAT_ID_RAW else None
except ValueError:
    ADMIN_CHAT_ID = None


@dataclass
class Option:
    text: str
    score: int


@dataclass
class Question:
    id: int
    category: str
    text: str
    options: List[Option]


# Упрощённая анкета: 25 вопросов, все по кликам
QUESTIONS: List[Question] = [
    # 1. Общие данные
    Question(
        id=1,
        category="Общие данные",
        text="Пол ребёнка:",
        options=[
            Option("Мужской", 0),
            Option("Женский", 0),
        ],
    ),
    Question(
        id=2,
        category="Общие данные",
        text="Возраст ребёнка:",
        options=[
            Option("До 3 лет", 2),
            Option("3–6 лет", 1),
            Option("7–12 лет", 1),
            Option("13+ лет", 0),
        ],
    ),
    Question(
        id=3,
        category="Общие данные",
        text="Место проживания:",
        options=[
            Option("Город", 0),
            Option("Сельская местность", 1),
        ],
    ),
    Question(
        id=4,
        category="Общие данные",
        text="Ребёнок единственный в семье?",
        options=[
            Option("Да", 0),
            Option("Нет, 2–3 детей", 1),
            Option("Нет, 4+ детей", 2),
        ],
    ),
    # 2. Питание и сладкое
    Question(
        id=5,
        category="Питание",
        text="Сколько раз в день ребёнок ест основную пищу?",
        options=[
            Option("1–2 раза", 2),
            Option("3–4 раза", 0),
            Option("5 и более раз", 1),
        ],
    ),
    Question(
        id=6,
        category="Питание",
        text="Сколько раз в день ребёнок перекусывает между приёмами пищи?",
        options=[
            Option("Почти не перекусывает", 0),
            Option("1–2 раза", 1),
            Option("3–4 раза", 2),
            Option("5 и более раз", 3),
        ],
    ),
    Question(
        id=7,
        category="Питание",
        text="Какие перекусы чаще всего?",
        options=[
            Option("Фрукты / овощи", 0),
            Option("Молочные (йогурт, сыр и т.п.)", 1),
            Option("Чипсы, печенье, выпечка", 2),
            Option("Конфеты, шоколад, желе", 3),
        ],
    ),
    Question(
        id=8,
        category="Питание",
        text="Сладкие напитки (соки, газировка и т.п.) в день:",
        options=[
            Option("Никогда", 0),
            Option("1–2 раза", 1),
            Option("3–4 раза", 2),
            Option("5 и более раз", 3),
        ],
    ),
    Question(
        id=9,
        category="Питание",
        text="Как часто ребёнок ест сладости (конфеты, торты, шоколад)?",
        options=[
            Option("Почти не ест", 0),
            Option("1–2 раза в неделю", 1),
            Option("3–5 раз в неделю", 2),
            Option("Каждый день", 3),
        ],
    ),
    Question(
        id=10,
        category="Питание",
        text="Как часто ребёнок ест липкую пищу (ириски, тянучки, клейкий рис и т.п.)?",
        options=[
            Option("Редко", 0),
            Option("1–3 раза в неделю", 1),
            Option("4–6 раз в неделю", 2),
            Option("Каждый день", 3),
        ],
    ),
    # 3. Привычки перед сном
    Question(
        id=11,
        category="Привычки",
        text="Есть ли у ребёнка привычка есть перед сном?",
        options=[
            Option("Никогда", 0),
            Option("1–2 раза в неделю", 1),
            Option("3–5 раз в неделю", 2),
            Option("Каждый день", 3),
        ],
    ),
    Question(
        id=12,
        category="Привычки",
        text="Если ребёнок ест перед сном, что чаще всего?",
        options=[
            Option("Не ест перед сном", 0),
            Option("Молоко без сахара", 1),
            Option("Печенье / сладкая выпечка", 3),
            Option("Фрукты", 1),
        ],
    ),
    Question(
        id=13,
        category="Гигиена",
        text="Чистит ли ребёнок зубы перед сном?",
        options=[
            Option("Всегда", 0),
            Option("Иногда", 2),
            Option("Почти никогда", 3),
        ],
    ),
    Question(
        id=14,
        category="Гигиена",
        text="Как часто ребёнок в целом чистит зубы?",
        options=[
            Option("2 раза в день и более", 0),
            Option("1 раз в день", 1),
            Option("Реже, чем раз в день", 3),
        ],
    ),
    # 4. Овощи и полезные продукты
    Question(
        id=15,
        category="Питание",
        text="Примерная доля овощей в рационе ребёнка:",
        options=[
            Option("Менее 20%", 3),
            Option("20–40%", 2),
            Option("40–60%", 1),
            Option("Более 60%", 0),
        ],
    ),
    Question(
        id=16,
        category="Питание",
        text="Как часто ребёнок ест молочные продукты (йогурт, сыр и т.п.)?",
        options=[
            Option("Каждый день, в достаточном количестве", 0),
            Option("4–6 раз в неделю", 1),
            Option("1–3 раза в неделю", 2),
            Option("Почти не ест", 3),
        ],
    ),
    # 5. Состояние зубов и визиты к врачу
    Question(
        id=17,
        category="Состояние зубов",
        text="Регулярно ли ребёнок посещает стоматолога (раз в 6 месяцев)?",
        options=[
            Option("Да", 0),
            Option("Только при боли", 2),
            Option("Очень редко / почти не ходим", 3),
        ],
    ),
    Question(
        id=18,
        category="Состояние зубов",
        text="Как Вы оцениваете текущее состояние зубов ребёнка?",
        options=[
            Option("Очень здоровые, без проблем", 0),
            Option("Лёгкий кариес, не мешает", 1),
            Option("Есть кариес, нужно лечение", 2),
            Option("Есть серьёзные проблемы (боль, гной и т.п.)", 3),
        ],
    ),
    Question(
        id=19,
        category="Знания и отношение",
        text="Ограничиваете ли Вы сладости и сладкие напитки ребёнка?",
        options=[
            Option("Всегда контролирую", 0),
            Option("Иногда ограничиваю", 1),
            Option("Редко думаю об этом", 2),
            Option("Почти не ограничиваю", 3),
        ],
    ),
    Question(
        id=20,
        category="Знания и отношение",
        text="Учите ли Вы ребёнка правильной чистке зубов?",
        options=[
            Option("Регулярно, показываю технику", 0),
            Option("Иногда напоминаю", 1),
            Option("Редко говорю об этом", 2),
            Option("Практически не обсуждаем", 3),
        ],
    ),
    # Дополнительные вопросы
    Question(
        id=21,
        category="Привычки",
        text="Есть ли у ребёнка привычка есть во время просмотра ТВ или игр на телефоне?",
        options=[
            Option("Всегда", 3),
            Option("Часто", 2),
            Option("Редко", 1),
            Option("Никогда", 0),
        ],
    ),
    Question(
        id=22,
        category="Питание",
        text="Как часто ребёнок ест кислые продукты (лимон, кислые сливы и т.п.)?",
        options=[
            Option("Почти никогда", 0),
            Option("1–2 раза в неделю", 1),
            Option("3–5 раз в неделю", 2),
            Option("Каждый день", 3),
        ],
    ),
    Question(
        id=23,
        category="Гигиена",
        text="Что ребёнок обычно делает после употребления сладкой или кислой пищи?",
        options=[
            Option("Сразу полощет рот водой", 0),
            Option("Полощет рот через некоторое время", 1),
            Option("Ничего не делает", 3),
            Option("Сразу чистит зубы", 1),
        ],
    ),
    Question(
        id=24,
        category="Состояние зубов",
        text="Была ли у ребёнка зубная боль за последний год?",
        options=[
            Option("Никогда", 0),
            Option("1–2 раза в год", 1),
            Option("3 раза в год и чаще", 3),
        ],
    ),
    Question(
        id=25,
        category="Знания и отношение",
        text="Знаете ли Вы о влиянии диеты на здоровье зубов детей?",
        options=[
            Option("Очень много", 0),
            Option("Немного", 1),
            Option("Очень мало", 2),
            Option("Совсем не знаю", 3),
        ],
    ),
]


class SurveyState:
    def __init__(self) -> None:
        self.current_index: int = 0
        self.total_score: int = 0
        self.answers: List[Dict[str, str]] = []
        self.finished: bool = False
        self.result_status: Optional[str] = None


bot = telebot.TeleBot(BOT_TOKEN)

# Память в процессе: для тестового задания достаточно
user_states: Dict[int, SurveyState] = {}


DISCLAIMER_TEXT = (
    "Это не медицинский диагноз, а **ориентировочная оценка** риска проблем "
    "полости рта ребёнка.\n\n"
    "Результаты анкеты не заменяют очный осмотр стоматолога. "
    "При любых жалобах или сомнениях обязательно запишитесь на приём к врачу."
)


def get_or_create_state(user_id: int) -> SurveyState:
    state = user_states.get(user_id)
    if state is None:
        state = SurveyState()
        user_states[user_id] = state
    return state


def build_question_markup(q_index: int) -> types.InlineKeyboardMarkup:
    q = QUESTIONS[q_index]
    markup = types.InlineKeyboardMarkup(row_width=1)
    buttons = []
    for opt_idx, opt in enumerate(q.options):
        callback_data = f"q:{q_index}:{opt_idx}"
        buttons.append(types.InlineKeyboardButton(text=opt.text, callback_data=callback_data))
    markup.add(*buttons)
    return markup


def score_to_status(score: int) -> str:
    if score <= 10:
        return "ЛЁГКИЕ НАРУШЕНИЯ"
    if 11 <= score <= 20:
        return "УМЕРЕННЫЕ НАРУШЕНИЯ"
    return "ТЯЖЁЛЫЕ НАРУШЕНИЯ"


def build_result_text(state: SurveyState) -> str:
    status = state.result_status or score_to_status(state.total_score)
    base = f"Ваш результат: *{state.total_score} баллов*\nСтатус: *{status}*\n\n"

    if status == "ЛЁГКИЕ НАРУШЕНИЯ":
        recommendations = (
            "Сейчас риск проблем с зубами у ребёнка невысокий, но есть моменты для улучшения.\n\n"
            "Рекомендуем:\n"
            "• Чистить зубы 2 раза в день не менее 2 минут.\n"
            "• Ограничить частые перекусы сладким и сладкие напитки.\n"
            "• Добавить в рацион овощи и продукты, богатые кальцием.\n"
            "• Посещать стоматолога профилактически 1 раз в 6 месяцев."
        )
    elif status == "УМЕРЕННЫЕ НАРУШЕНИЯ":
        recommendations = (
            "Риск проблем с зубами у ребёнка *повышен*.\n\n"
            "Обязательно:\n"
            "• Снизить количество сладостей и липких конфет, особенно перед сном.\n"
            "• Строго соблюдать гигиену полости рта (2 раза в день, с контролем со стороны взрослого).\n"
            "• Добавить в рацион овощи, молочные продукты, продукты с витамином C.\n"
            "• Записаться на профилактический осмотр к стоматологу в ближайшее время."
        )
    else:
        recommendations = (
            "Выявлен *высокий риск* серьёзных стоматологических проблем.\n\n"
            "Рекомендуем:\n"
            "• В ближайшее время записаться на очный приём к детскому стоматологу.\n"
            "• Не откладывать обращение при наличии боли, отёка, неприятного запаха изо рта.\n"
            "• После консультации врача строго соблюдать назначенный план лечения и гигиены."
        )

    return base + recommendations


def ask_phone(chat_id: int) -> None:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    phone_button = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    skip_button = types.KeyboardButton(text="Не оставлять телефон")
    markup.add(phone_button)
    markup.add(skip_button)
    bot.send_message(
        chat_id,
        "Если хотите, мы можем связаться с вами для подробной консультации.\n\n"
        "Нажмите кнопку, чтобы отправить номер телефона, или выберите «Не оставлять телефон».",
        reply_markup=markup,
    )


@bot.message_handler(commands=["start"])
def handle_start(message: types.Message) -> None:
    chat_id = message.chat.id
    state = get_or_create_state(chat_id)
    state.current_index = 0
    state.total_score = 0
    state.answers = []
    state.finished = False
    state.result_status = None

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Согласен, начать", callback_data="start_survey"))
    bot.send_message(chat_id, DISCLAIMER_TEXT, parse_mode="Markdown", reply_markup=markup)


def send_question(chat_id: int, q_index: int) -> None:
    q = QUESTIONS[q_index]
    text = f"Вопрос {q_index + 1} из {len(QUESTIONS)}\n\n{q.text}"
    markup = build_question_markup(q_index)
    bot.send_message(chat_id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "start_survey")
def callback_start_survey(call: types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    state = get_or_create_state(chat_id)
    state.current_index = 0
    state.total_score = 0
    state.answers = []
    state.finished = False
    state.result_status = None
    bot.answer_callback_query(call.id)
    send_question(chat_id, 0)


@bot.callback_query_handler(func=lambda call: call.data.startswith("q:"))
def callback_answer_question(call: types.CallbackQuery) -> None:
    chat_id = call.message.chat.id
    state = get_or_create_state(chat_id)

    try:
        _, q_index_str, opt_index_str = call.data.split(":")
        q_index = int(q_index_str)
        opt_index = int(opt_index_str)
    except (ValueError, IndexError):
        bot.answer_callback_query(call.id, text="Ошибка обработки ответа.")
        return

    if q_index < 0 or q_index >= len(QUESTIONS):
        bot.answer_callback_query(call.id, text="Вопрос не найден.")
        return

    question = QUESTIONS[q_index]
    if opt_index < 0 or opt_index >= len(question.options):
        bot.answer_callback_query(call.id, text="Вариант ответа не найден.")
        return

    option = question.options[opt_index]

    state.total_score += option.score
    state.answers.append(
        {
            "question": question.text,
            "answer": option.text,
            "score": str(option.score),
            "category": question.category,
        }
    )
    state.current_index = q_index + 1

    bot.answer_callback_query(call.id)

    if state.current_index < len(QUESTIONS):
        send_question(chat_id, state.current_index)
    else:
        state.finished = True
        state.result_status = score_to_status(state.total_score)
        report_text = build_result_text(state)
        bot.send_message(chat_id, report_text, parse_mode="Markdown")

        # Условное "сохранение" отчёта: можно заменить на запись в файл/БД
        print(
            f"[REPORT] chat_id={chat_id} score={state.total_score} status={state.result_status} "
            f"answers={len(state.answers)}"
        )

        ask_phone(chat_id)


@bot.message_handler(content_types=["contact"])
def handle_contact(message: types.Message) -> None:
    chat_id = message.chat.id
    contact = message.contact
    state = get_or_create_state(chat_id)

    bot.send_message(chat_id, "Спасибо! Мы получили ваш номер телефона.", reply_markup=types.ReplyKeyboardRemove())

    if ADMIN_CHAT_ID:
        text_lines = [
            "Новый контакт от пользователя анкеты:",
            f"Имя: {contact.first_name or ''} {contact.last_name or ''}".strip(),
            f"Телефон: {contact.phone_number}",
            f"Telegram username: @{message.from_user.username}" if message.from_user.username else "",
            f"Итоговый балл: {state.total_score}",
            f"Статус: {state.result_status or score_to_status(state.total_score)}",
        ]
        text = "\n".join(line for line in text_lines if line)
        bot.send_message(ADMIN_CHAT_ID, text)


@bot.message_handler(func=lambda m: m.text == "Не оставлять телефон")
def handle_skip_phone(message: types.Message) -> None:
    bot.send_message(
        message.chat.id,
        "Спасибо за прохождение анкеты! Вы всегда можете вернуться к боту командой /start.",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@bot.message_handler(commands=["help"])
def handle_help(message: types.Message) -> None:
    bot.send_message(
        message.chat.id,
        "Этот бот поможет ориентировочно оценить состояние полости рта ребёнка.\n\n"
        "• /start — начать анкету заново\n"
        "• Все ответы выбираются только кнопками\n"
        "• В конце вы можете отправить номер телефона для связи",
    )


def main() -> None:
    bot.infinity_polling(skip_pending=True)


if __name__ == "__main__":
    main()

