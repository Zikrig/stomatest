import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import telebot
from telebot import types


BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS_RAW = os.environ.get("ADMIN_IDS", "")
CONFIG_PATH = os.environ.get("CONFIG_PATH", "config.json")

if not BOT_TOKEN:
    raise RuntimeError("Environment variable BOT_TOKEN is required")

ADMIN_IDS: List[int] = []
for part in ADMIN_IDS_RAW.replace(" ", "").split(","):
    part = part.strip()
    if part:
        try:
            ADMIN_IDS.append(int(part))
        except ValueError:
            pass


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

DEFAULT_WELCOME_TEXT = (
    "Это не медицинский диагноз, а **ориентировочная оценка** риска проблем "
    "полости рта ребёнка.\n\n"
    "Результаты анкеты не заменяют очный осмотр стоматолога. "
    "При любых жалобах или сомнениях обязательно запишитесь на приём к врачу."
)


def _config_path() -> Path:
    return Path(CONFIG_PATH)


def _load_config() -> Dict[str, Any]:
    p = _config_path()
    if not p.exists():
        return {"welcome_text": None, "welcome_photo": None, "questions": []}
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = {}
    if "questions" not in data:
        data["questions"] = []
    while len(data["questions"]) < len(QUESTIONS):
        data["questions"].append({"text": None, "photo": None})
    return data


def _save_config(data: Dict[str, Any]) -> None:
    p = _config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_welcome_text() -> str:
    data = _load_config()
    t = data.get("welcome_text")
    # Не показывать команды как приветствие (если админ случайно сохранил /admin или /start)
    if t and t.strip().startswith("/"):
        return DEFAULT_WELCOME_TEXT
    return t if t else DEFAULT_WELCOME_TEXT


def get_welcome_photo() -> Optional[str]:
    return _load_config().get("welcome_photo")


def get_question_display_text(q_index: int) -> str:
    q = QUESTIONS[q_index]
    data = _load_config()
    questions = data.get("questions") or []
    if q_index < len(questions) and questions[q_index].get("text"):
        return questions[q_index]["text"]
    return q.text


def get_question_photo(q_index: int) -> Optional[str]:
    data = _load_config()
    questions = data.get("questions") or []
    if q_index < len(questions):
        return questions[q_index].get("photo")
    return None


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

# Админ: ожидание ввода (текст или фото)
# {"action": "welcome_text" | "welcome_photo" | "question_text" | "question_photo", "question_index": int?}
admin_states: Dict[int, Dict[str, Any]] = {}


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


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


def _admin_main_markup() -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(types.InlineKeyboardButton("Приветствие: текст", callback_data="admin:welcome_text"))
    m.add(types.InlineKeyboardButton("Приветствие: картинка", callback_data="admin:welcome_photo"))
    if get_welcome_photo():
        m.add(types.InlineKeyboardButton("Приветствие: убрать картинку", callback_data="admin:welcome_photo_clear"))
    m.add(types.InlineKeyboardButton("Список вопросов (1–25)", callback_data="admin:question_list"))
    return m


def _admin_question_list_markup() -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=5)
    row = []
    for i in range(len(QUESTIONS)):
        row.append(types.InlineKeyboardButton(str(i + 1), callback_data=f"admin:q:{i}"))
        if len(row) == 5:
            m.add(*row)
            row = []
    if row:
        m.add(*row)
    m.add(types.InlineKeyboardButton("← В меню", callback_data="admin:menu"))
    return m


def _admin_question_submenu_markup(q_index: int) -> types.InlineKeyboardMarkup:
    m = types.InlineKeyboardMarkup(row_width=1)
    m.add(types.InlineKeyboardButton("Изменить текст", callback_data=f"admin:q:{q_index}:text"))
    m.add(types.InlineKeyboardButton("Изменить картинку", callback_data=f"admin:q:{q_index}:photo"))
    data = _load_config()
    questions = data.get("questions") or []
    if q_index < len(questions) and questions[q_index].get("photo"):
        m.add(types.InlineKeyboardButton("Убрать картинку", callback_data=f"admin:q:{q_index}:clear"))
    m.add(types.InlineKeyboardButton("← К списку вопросов", callback_data="admin:question_list"))
    m.add(types.InlineKeyboardButton("← В меню", callback_data="admin:menu"))
    return m


def _admin_send_menu(chat_id: int, text: str = "Админка. Выберите действие:") -> None:
    bot.send_message(chat_id, text, reply_markup=_admin_main_markup())


def _admin_send_welcome_preview(chat_id: int) -> None:
    """Отправляет текущий вид приветствия (как видят пользователи), без кнопок."""
    welcome_text = get_welcome_text()
    photo_file_id = get_welcome_photo()
    if photo_file_id:
        caption = welcome_text[:PHOTO_CAPTION_MAX] + ("…" if len(welcome_text) > PHOTO_CAPTION_MAX else "")
        bot.send_photo(chat_id, photo_file_id, caption=caption, parse_mode="Markdown")
        if len(welcome_text) > PHOTO_CAPTION_MAX:
            bot.send_message(chat_id, welcome_text, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, welcome_text, parse_mode="Markdown")


def _admin_send_question_preview(chat_id: int, q_index: int) -> None:
    """Отправляет текущий вид вопроса (как видят пользователи), без кнопок ответов."""
    display_text = get_question_display_text(q_index)
    text = f"Вопрос {q_index + 1} из {len(QUESTIONS)}\n\n{display_text}"
    photo_file_id = get_question_photo(q_index)
    if photo_file_id:
        caption = text[:PHOTO_CAPTION_MAX] + ("…" if len(text) > PHOTO_CAPTION_MAX else "")
        bot.send_photo(chat_id, photo_file_id, caption=caption)
        if len(text) > PHOTO_CAPTION_MAX:
            bot.send_message(chat_id, text)
    else:
        bot.send_message(chat_id, text)


# Ограничение длины подписи к фото в Telegram (API)
PHOTO_CAPTION_MAX = 1024


@bot.message_handler(func=lambda m: m.from_user and m.from_user.id in admin_states)
def handle_admin_input(message: types.Message) -> None:
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        admin_states.pop(user_id, None)
        return
    state = admin_states.get(user_id)
    if not state:
        return
    chat_id = message.chat.id
    action = state.get("action")
    # Сообщение, начинающееся с /, считаем отменой — не сохраняем как контент
    if message.text and message.text.strip().startswith("/"):
        admin_states.pop(user_id, None)
        bot.send_message(chat_id, "Отменено. Изменения не сохранены.")
        _admin_send_menu(chat_id)
        return
    data = _load_config()
    if action == "welcome_text":
        if message.text is not None:
            data["welcome_text"] = message.text
            _save_config(data)
            admin_states.pop(user_id, None)
            bot.send_message(chat_id, "✅ Изменения приняты. Приветствие теперь отображается так:")
            _admin_send_welcome_preview(chat_id)
            _admin_send_menu(chat_id)
        return
    if action == "welcome_photo":
        if message.photo:
            data["welcome_photo"] = message.photo[-1].file_id
            _save_config(data)
            admin_states.pop(user_id, None)
            bot.send_message(chat_id, "✅ Изменения приняты. Приветствие теперь отображается так:")
            _admin_send_welcome_preview(chat_id)
            _admin_send_menu(chat_id)
        return
    if action == "question_text":
        q_index = state.get("question_index", 0)
        if message.text is not None and 0 <= q_index < len(QUESTIONS):
            while len(data.get("questions", [])) <= q_index:
                data.setdefault("questions", []).append({"text": None, "photo": None})
            data["questions"][q_index]["text"] = message.text
            _save_config(data)
            admin_states.pop(user_id, None)
            bot.send_message(chat_id, f"✅ Изменения приняты. Вопрос {q_index + 1} теперь отображается так:")
            _admin_send_question_preview(chat_id, q_index)
            _admin_send_menu(chat_id)
        return
    if action == "question_photo":
        q_index = state.get("question_index", 0)
        if message.photo and 0 <= q_index < len(QUESTIONS):
            while len(data.get("questions", [])) <= q_index:
                data.setdefault("questions", []).append({"text": None, "photo": None})
            data["questions"][q_index]["photo"] = message.photo[-1].file_id
            _save_config(data)
            admin_states.pop(user_id, None)
            bot.send_message(chat_id, f"✅ Изменения приняты. Вопрос {q_index + 1} теперь отображается так:")
            _admin_send_question_preview(chat_id, q_index)
            _admin_send_menu(chat_id)
        return


@bot.message_handler(commands=["admin"])
def handle_admin_command(message: types.Message) -> None:
    if not message.from_user:
        return
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "Доступ запрещён.")
        return
    _admin_send_menu(message.chat.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("admin:"))
def handle_admin_callback(call: types.CallbackQuery) -> None:
    if not call.from_user or not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, text="Доступ запрещён.")
        return
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    parts = call.data.split(":")
    bot.answer_callback_query(call.id)
    if parts[1] == "menu":
        admin_states.pop(user_id, None)
        try:
            bot.edit_message_text("Админка. Выберите действие:", chat_id, call.message.message_id, reply_markup=_admin_main_markup())
        except Exception:
            bot.send_message(chat_id, "Админка. Выберите действие:", reply_markup=_admin_main_markup())
        return
    if parts[1] == "welcome_text":
        admin_states[user_id] = {"action": "welcome_text"}
        bot.send_message(chat_id, "Текущий вид приветствия (как видят пользователи):")
        _admin_send_welcome_preview(chat_id)
        bot.send_message(chat_id, "Отправьте новый текст приветствия (поддерживается Markdown). Для отмены — /admin.")
        return
    if parts[1] == "welcome_photo":
        admin_states[user_id] = {"action": "welcome_photo"}
        bot.send_message(chat_id, "Текущий вид приветствия (как видят пользователи):")
        _admin_send_welcome_preview(chat_id)
        bot.send_message(chat_id, "Отправьте новую картинку для приветствия.")
        return
    if parts[1] == "welcome_photo_clear":
        data = _load_config()
        data["welcome_photo"] = None
        _save_config(data)
        bot.send_message(chat_id, "✅ Изменения приняты. Приветствие теперь отображается так:")
        _admin_send_welcome_preview(chat_id)
        try:
            bot.edit_message_text("Админка. Выберите действие:", chat_id, call.message.message_id, reply_markup=_admin_main_markup())
        except Exception:
            _admin_send_menu(chat_id)
        return
    if parts[1] == "question_list":
        try:
            bot.edit_message_text("Выберите номер вопроса (1–25):", chat_id, call.message.message_id, reply_markup=_admin_question_list_markup())
        except Exception:
            bot.send_message(chat_id, "Выберите номер вопроса (1–25):", reply_markup=_admin_question_list_markup())
        return
    if parts[1] == "q":
        if len(parts) == 3:
            q_index = int(parts[2])
            if 0 <= q_index < len(QUESTIONS):
                bot.send_message(chat_id, f"Вопрос {q_index + 1}. Текущий вид (как видят пользователи):")
                _admin_send_question_preview(chat_id, q_index)
                try:
                    bot.edit_message_text(
                        f"Вопрос {q_index + 1}. Что изменить?",
                        chat_id,
                        call.message.message_id,
                        reply_markup=_admin_question_submenu_markup(q_index),
                    )
                except Exception:
                    bot.send_message(chat_id, f"Вопрос {q_index + 1}. Что изменить?", reply_markup=_admin_question_submenu_markup(q_index))
            return
        if len(parts) == 4:
            q_index = int(parts[2])
            sub = parts[3]
            if sub == "text":
                admin_states[user_id] = {"action": "question_text", "question_index": q_index}
                bot.send_message(chat_id, f"Вопрос {q_index + 1}. Текущий вид:")
                _admin_send_question_preview(chat_id, q_index)
                bot.send_message(chat_id, f"Отправьте новый текст для вопроса {q_index + 1}.")
                return
            if sub == "photo":
                admin_states[user_id] = {"action": "question_photo", "question_index": q_index}
                bot.send_message(chat_id, f"Вопрос {q_index + 1}. Текущий вид:")
                _admin_send_question_preview(chat_id, q_index)
                bot.send_message(chat_id, f"Отправьте картинку для вопроса {q_index + 1}.")
                return
            if sub == "clear" and 0 <= q_index < len(QUESTIONS):
                data = _load_config()
                while len(data.get("questions", [])) <= q_index:
                    data.setdefault("questions", []).append({"text": None, "photo": None})
                data["questions"][q_index]["photo"] = None
                _save_config(data)
                bot.send_message(chat_id, f"✅ Изменения приняты. Вопрос {q_index + 1} теперь отображается так:")
                _admin_send_question_preview(chat_id, q_index)
                try:
                    bot.edit_message_text("Админка. Выберите действие:", chat_id, call.message.message_id, reply_markup=_admin_main_markup())
                except Exception:
                    _admin_send_menu(chat_id)
                return


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
    welcome_text = get_welcome_text()
    photo_file_id = get_welcome_photo()
    if photo_file_id:
        if len(welcome_text) <= PHOTO_CAPTION_MAX:
            bot.send_photo(chat_id, photo_file_id, caption=welcome_text, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.send_photo(chat_id, photo_file_id, caption=welcome_text[: PHOTO_CAPTION_MAX - 1] + "…", parse_mode="Markdown")
            bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup)


def send_question(chat_id: int, q_index: int) -> None:
    display_text = get_question_display_text(q_index)
    text = f"Вопрос {q_index + 1} из {len(QUESTIONS)}\n\n{display_text}"
    markup = build_question_markup(q_index)
    photo_file_id = get_question_photo(q_index)
    if photo_file_id:
        if len(text) <= PHOTO_CAPTION_MAX:
            bot.send_photo(chat_id, photo_file_id, caption=text, reply_markup=markup)
        else:
            bot.send_photo(chat_id, photo_file_id, caption=f"Вопрос {q_index + 1} из {len(QUESTIONS)}")
            bot.send_message(chat_id, display_text, reply_markup=markup)
    else:
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

    if ADMIN_IDS:
        text_lines = [
            "Новый контакт от пользователя анкеты:",
            f"Имя: {contact.first_name or ''} {contact.last_name or ''}".strip(),
            f"Телефон: {contact.phone_number}",
            f"Telegram username: @{message.from_user.username}" if message.from_user.username else "",
            f"Итоговый балл: {state.total_score}",
            f"Статус: {state.result_status or score_to_status(state.total_score)}",
        ]
        text = "\n".join(line for line in text_lines if line)
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, text)
            except Exception:
                pass


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

