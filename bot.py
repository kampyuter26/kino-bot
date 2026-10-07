import json
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


# =========================
# BOT TOKEN
# =========================

TOKEN = os.environ["BOT_TOKEN"]


# =========================
# ADMIN ID
# =========================

ADMIN_ID = 6522573426


# =========================
# KANALLAR
# =========================

CHANNELS = [
    "@Turk_seriallar_uzbsub",
    "@luna_uzbsub",
    "@Drama_uzbsub",
]


# =========================
# OBUNANI TEKSHIRISH
# =========================

async def is_subscribed(user_id, context):

    for channel in CHANNELS:

        try:

            member = await context.bot.get_chat_member(
                chat_id=channel,
                user_id=user_id
            )

            if member.status in ["left", "kicked"]:
                return False

        except Exception:
            return False

    return True


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [

        [
            InlineKeyboardButton(
                "📢 Turk seriallar",
                url="https://t.me/Turk_seriallar_uzbsub"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 Luna",
                url="https://t.me/luna_uzbsub"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 Drama",
                url="https://t.me/Drama_uzbsub"
            )
        ],

        [
            InlineKeyboardButton(
                "✅ Tekshirish",
                callback_data="check_sub"
            )
        ]

    ]

    await update.message.reply_text(

        "🎬 Kino botiga xush kelibsiz!\n\n"
        "Kino olish uchun quyidagi 3 ta kanalga a'zo bo'ling.\n"
        "Keyin «✅ Tekshirish» tugmasini bosing.",

        reply_markup=InlineKeyboardMarkup(keyboard)

    )


# =========================
# OBUNANI QAYTA TEKSHIRISH
# =========================

async def check_subscription(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not await is_subscribed(
        query.from_user.id,
        context
    ):

        await query.message.reply_text(

            "❌ Siz hali barcha kanallarga a'zo bo'lmagansiz.\n\n"
            "3 ta kanalga ham a'zo bo'ling va "
            "yana «✅ Tekshirish» tugmasini bosing."

        )

        return

    await query.message.reply_text(

        "✅ Hammasi joyida!\n\n"
        "🎬 Endi kino kodini yuboring.\n\n"
        "Masalan: 125"

    )


# =========================
# MY ID
# =========================

async def myid(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(

        f"Sizning Telegram ID'ingiz:\n\n"
        f"{update.effective_user.id}"

    )


# =========================
# KINO QO'SHISH
# =========================

async def add_movie(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Faqat admin ishlata oladi
    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Siz admin emassiz."
        )

        return

    # Kod yozilmagan bo'lsa
    if not context.args:

        await update.message.reply_text(

            "❗ Kino kodini yozing.\n\n"
            "Masalan:\n"
            "/add 125"

        )

        return

    code = context.args[0]

    # Keyingi yuboriladigan videoga kodni bog'laymiz
    context.user_data["add_movie_code"] = code

    await update.message.reply_text(

        f"🎬 Kino kodi: {code}\n\n"
        "Endi videoni shu yerga yuboring."

    )


# =========================
# KINO O'CHIRISH
# =========================

async def delete_movie(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Faqat admin ishlata oladi
    if update.effective_user.id != ADMIN_ID:

        await update.message.reply_text(
            "❌ Siz admin emassiz."
        )

        return

    # Kod yozilmagan bo'lsa
    if not context.args:

        await update.message.reply_text(

            "❗ O'chiriladigan kino kodini yozing.\n\n"
            "Masalan:\n"
            "/delete 125"

        )

        return

    code = context.args[0]

    # movies.json ni ochamiz
    try:

        with open(
            "movies.json",
            "r",
            encoding="utf-8"
        ) as f:

            movies = json.load(f)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        movies = {}

    # Kino mavjudligini tekshiramiz
    if code not in movies:

        await update.message.reply_text(

            f"❌ {code} kodli kino topilmadi."

        )

        return

    # Kinoni o'chiramiz
    del movies[code]

    # movies.json ga qayta yozamiz
    with open(
        "movies.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            movies,
            f,
            ensure_ascii=False,
            indent=4
        )

    await update.message.reply_text(

        f"🗑 Kino o'chirildi!\n\n"
        f"🎬 Kino kodi: {code}"

    )


# =========================
# VIDEONI SAQLASH
# =========================

async def save_movie(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Faqat admin
    if update.effective_user.id != ADMIN_ID:
        return

    # Oldindan kino kodi berilganmi?
    code = context.user_data.get("add_movie_code")

    if not code:
        return

    # Video olish
    video = update.message.video

    if not video:
        return

    # movies.json ni ochamiz
    try:

        with open(
            "movies.json",
            "r",
            encoding="utf-8"
        ) as f:

            movies = json.load(f)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        movies = {}

    # Video file_id sini saqlaymiz
    movies[code] = video.file_id

    # movies.json ga yozamiz
    with open(
        "movies.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            movies,
            f,
            ensure_ascii=False,
            indent=4
        )

    # Kodni tozalaymiz
    context.user_data.pop(
        "add_movie_code",
        None
    )

    await update.message.reply_text(

        f"✅ Kino muvaffaqiyatli saqlandi!\n\n"
        f"🎬 Kino kodi: {code}"

    )


# =========================
# KINO KODINI QABUL QILISH
# =========================

async def kino_kodi(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Obunani tekshiramiz
    if not await is_subscribed(
        update.effective_user.id,
        context
    ):

        keyboard = [

            [
                InlineKeyboardButton(
                    "📢 Turk seriallar",
                    url="https://t.me/Turk_seriallar_uzbsub"
                )
            ],

            [
                InlineKeyboardButton(
                    "📢 Luna",
                    url="https://t.me/luna_uzbsub"
                )
            ],

            [
                InlineKeyboardButton(
                    "📢 Drama",
                    url="https://t.me/Drama_uzbsub"
                )
            ],

            [
                InlineKeyboardButton(
                    "✅ Tekshirish",
                    callback_data="check_sub"
                )
            ]

        ]

        await update.message.reply_text(

            "❌ Kino olish uchun avval "
            "3 ta kanalga a'zo bo'ling!",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )

        )

        return

    # Foydalanuvchi yuborgan kod
    code = update.message.text.strip()

    # movies.json ni ochamiz
    try:

        with open(
            "movies.json",
            "r",
            encoding="utf-8"
        ) as f:

            movies = json.load(f)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        movies = {}

    # Kino topilmasa
    if code not in movies:

        await update.message.reply_text(

            "❌ Bunday kino kodi topilmadi.\n\n"
            "Kino kodini to'g'ri yuboring."

        )

        return

    # Kino yuboriladi
    await update.message.reply_video(

        video=movies[code],

        caption=f"🎬 Kino kodi: {code}"

    )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

app = Application.builder().token(TOKEN).build()


# /start
app.add_handler(
    CommandHandler("start", start)
)


# /myid
app.add_handler(
    CommandHandler("myid", myid)
)


# /add
app.add_handler(
    CommandHandler("add", add_movie)
)


# /delete
app.add_handler(
    CommandHandler("delete", delete_movie)
)


# Tekshirish tugmasi
app.add_handler(
    CallbackQueryHandler(
        check_subscription,
        pattern="^check_sub$"
    )
)


# Admin yuborgan video
app.add_handler(
    MessageHandler(
        filters.VIDEO,
        save_movie
    )
)


# Kino kodi
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        kino_kodi
    )
)


# Ishga tushganini ko'rsatadi
print("Bot ishga tushdi...")


# Botni ishga tushirish
app.run_polling()
