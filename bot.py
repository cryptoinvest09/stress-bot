import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
)
BOT_TOKEN = os.getenv("BOT_TOKEN")

PRICE_TEXT = "3999 ₸"
KASPI_PHONE = "+7 777 030 9727"
WHATSAPP_PHONE = "+7 777 030 9727"

# 20 questions * max 3 = 60
LOW_MAX = 20
MID_MAX = 40

# Conversation states
ASKING, AFTER_RESULT = range(2)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------- QUESTIONS ----------------
QUESTIONS = [
    "1. Соңғы күндері өзіңізді себепсіз мазасыз сезінесіз бе?",
    "2. Ұйқыға кету немесе түнде оянып кету жиі бола ма?",
    "3. Күнделікті істерге күшіңіз азайып, тез шаршайсыз ба?",
    "4. Ұсақ нәрселерге жиі ашуланасыз ба?",
    "5. Бас, мойын немесе арқа бұлшықеттерінде кернеу сезесіз бе?",
    "6. Ойыңызды жинақтау қиын болып жүр ме?",
    "7. Жүрек қағуы немесе ішкі қобалжу сезімі бола ма?",
    "8. Демалсаңыз да, толық сергіп кете алмайсыз ба?",
    "9. Көңіл-күйіңіз себепсіз түсіп кететін кездер бола ма?",
    "10. Қарапайым мәселелердің өзі ауыр болып көріне ме?",
    "11. Тәбетіңіз өзгерді ме (тым аз немесе тым көп жеу)?",
    "12. Көп нәрсені бақылауда ұстай алмай жатқандай сезінесіз бе?",
    "13. Болашақ туралы уайым жиі мазалай ма?",
    "14. Жұмысқа/оқуға назар аудару қиындады ма?",
    "15. Денеңізде діріл, мазасыздық немесе тыныш отыра алмау бар ма?",
    "16. Айналаңыздағы адамдармен сөйлескіңіз келмейтін кездер жиі бола ма?",
    "17. Соңғы кезде өзіңізді эмоциялық тұрғыдан қажығандай сезінесіз бе?",
    "18. Демалыс күнінен кейін де шаршау кетпей ме?",
    "19. Күн ішінде жиі кернеу, қысым немесе асығыстық сезімі болады ма?",
    "20. Соңғы апталарда стресс өмір сапаңызға әсер етіп жүр ме?",
]

OPTIONS = [
    ("Ешқашан (Мүлдем жоқ)", 1),
    ("Өте сирек", 2),
    ("Сирек", 3),
    ("Кейде", 4),
    ("Жиі", 5),
    ("Өте жиі", 6),
    ("Үнемі (Әрдайым)", 7),
]

# ---------------- HELPERS ----------------
def start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Бастау", callback_data="start_test")]
    ])

def option_keyboard(q_index: int):
    rows = []
    for idx, (title, score) in enumerate(OPTIONS):
        rows.append([InlineKeyboardButton(title, callback_data=f"ans:{q_index}:{score}")])
    return InlineKeyboardMarkup(rows)

def result_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💳 Нұсқаулықты алу — {PRICE_TEXT}", callback_data="buy_guide")],
        [InlineKeyboardButton("✅ Төледім", callback_data="paid")],
    ])

def score_text(total: int) -> str:
    # max = 60
    if total <= 60:
        return (
            f"Нәтиже: {total}/140\n\n"
            "🟢 Қалыпты деңгей\n"
            "Сізде стресс деңгейі төмен немесе бақылауда.\n\n"
            "Өмір салтыңызды сақтауды жалғастырыңыз."
        )

    elif total <= 100:
        return (
            f"Нәтиже: {total}/140\n\n"
            "🟡 Орташа стресс деңгейі\n"
            "Сізде жиналған стресс бар.\n\n"
            "Қазірден бастап демалыс, тыныс жаттығулары маңызды."
        )

    else:
        return (
            f"Нәтиже: {total}/140\n\n"
            "🔴 Жоғары стресс деңгейі\n"
            "Сізде айқын стресс байқалады.\n\n"
            "Маман көмегі пайдалы болуы мүмкін."
        )

async def send_question(query, context: ContextTypes.DEFAULT_TYPE):
    q_index = context.user_data.get("q_index", 0)
    text = QUESTIONS[q_index]
    await query.edit_message_text(
        text=text,
        reply_markup=option_keyboard(q_index)
    )

# ---------------- HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()

    text = (
        "Қайырлы күн! Мен — Елік Мадиқызының цифрлық көмекшісімін. 🩺\n\n"
        "Менің мақсатым — сіздің қазіргі эмоционалдық күйіңізді қысқа сауалнама арқылы бағалауға көмектесу.\n\n"
        "Ескерту: мен диагноз қоймаймын. Бұл тек ақпараттық өзін-өзі бағалау құралы.\n\n"
        "Бастау үшін төмендегі батырманы басыңыз."
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=start_keyboard())
    else:
        await update.callback_query.message.reply_text(text, reply_markup=start_keyboard())

    return ASKING

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    context.user_data["q_index"] = 0
    context.user_data["score"] = 0

    await send_question(query, context)
    return ASKING

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    data = query.data  # ans:q_index:score
    _, q_index_str, score_str = data.split(":")
    q_index = int(q_index_str)
    score = int(score_str)

    # safety check
    current_q = context.user_data.get("q_index", 0)
    if q_index != current_q:
        await query.answer("Ескі батырма басылды. Қайтадан жалғастырыңыз.", show_alert=True)
        return ASKING

    context.user_data["score"] = context.user_data.get("score", 0) + score
    context.user_data["q_index"] = current_q + 1

    if context.user_data["q_index"] >= len(QUESTIONS):
        total = context.user_data["score"]

        result_message = (
            score_text(total)
            + "\n\n"
            + f"📘 Егер сізге толық нұсқаулық керек болса, төлем сомасы: **{PRICE_TEXT}**\n"
            + f"Kaspi нөмірі: **{KASPI_PHONE}**\n\n"
            + "Төлем жасаған соң төмендегі **«Төледім»** батырмасын басыңыз."
        )

        await query.edit_message_text(
            text=result_message,
            reply_markup=result_keyboard(),
            parse_mode="Markdown"
        )
        return AFTER_RESULT

    await send_question(query, context)
    return ASKING

async def buy_guide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    text = (
        f"📘 Нұсқаулық бағасы: **{PRICE_TEXT}**\n"
        f"Kaspi нөмірі: **{KASPI_PHONE}**\n\n"
        "Төлем жасаған соң **«Төледім»** батырмасын басыңыз."
    )

    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=result_keyboard())
    return AFTER_RESULT

async def paid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    text = (
        "✅ Рақмет!\n\n"
        "Енді төмендегі WhatsApp нөміріне жазыңыз және **Kaspi төлем скринін** жіберіңіз:\n\n"
        f"📱 **{WHATSAPP_PHONE}**\n\n"
        "Хабарламада:\n"
        "1) төлем скринін,\n"
        "2) атыңызды,\n"
        "3) боттағы нәтижені қысқаша жібере аласыз.\n\n"
        "Тексеруден кейін сізге жеке WhatsApp топ сілтемесі жіберіледі."
    )

    await query.message.reply_text(text, parse_mode="Markdown")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = "Сауалнама тоқтатылды. Қайта бастау үшін /start жазыңыз."
    if update.message:
        await update.message.reply_text(text)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text)
    return ConversationHandler.END

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASKING: [
                CallbackQueryHandler(start_test, pattern="^start_test$"),
                CallbackQueryHandler(handle_answer, pattern=r"^ans:\d+:\d+$"),
            ],
            AFTER_RESULT: [
                CallbackQueryHandler(buy_guide, pattern="^buy_guide$"),
                CallbackQueryHandler(paid, pattern="^paid$"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.add_error_handler(error_handler)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
