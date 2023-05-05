from typing import Dict
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
import logging
from telegram.ext import (CommandHandler, MessageHandler, filters,  Application,
                           ContextTypes, ConversationHandler, CallbackQueryHandler)
from googletrans import Translator

import tracemalloc
tracemalloc.start()


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [
    ["Gramática", "Vocabulario básico"],
    ["Práctica", "Recursos adicionales"],
    ["Done"],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


# async def start(update, context):
#     await update.message.reply_text(
#         "Hola! ¿En qué puedo ayudarte?", reply_markup=markup
#     )
#     return CHOOSING

async def start(update, context: ContextTypes.DEFAULT_TYPE):

    if update.message:
        await update.message.reply_text("Hola! ¿En qué puedo ayudarte?",
                    reply_markup=markup)

    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Hola! ¿En qué puedo ayudarte?")
    return CHOOSING

def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

async def vocabulario(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Hola", callback_data="hola"),
            InlineKeyboardButton("Gato nene", callback_data="Gato nene"),
        ],
        [InlineKeyboardButton("¿Como estas?", callback_data="¿Como estas?")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Empecemos. ¿Qué palabra te gustaría aprender hoy? Puedes escribir la palabra o seleccionarla de la lista:"
        ,reply_markup = reply_markup)
    

async def options(update, context):
    query = update.callback_query
    await query.answer()
    option_selected = query.data

    # Llamar a la función "selected_option" para manejar la selección del usuario
    next_state = await selected_option(update, context, option_selected)

    return next_state

async def selected_option(update, context, option_selected):
    # Crear un objeto Translator
    translator = Translator()

    # Traducir el texto al inglés
    translated_text = translator.translate(str(option_selected), src="es", dest="en")

    # Responder al usuario con la traducción
    await update.callback_query.edit_message_text(
        text=f"La palabra que seleccionaste se traduce como: {translated_text.text}"
    )

    # Enviar el mensaje del menú principal
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Hola! ¿En qué puedo ayudarte?",
            reply_markup=markup
        )

    # Retornar al menú principal
    return CHOOSING



# async def selected_option(update, context, option_selected):
#     # Crear un objeto Translator
#     translator = Translator()

#     # Traducir el texto al inglés
#     translated_text = translator.translate(str(option_selected), src="es", dest="en")

#     # Crear el teclado de opciones
#     keyboard = [
#         [
#             InlineKeyboardButton("Gramática", callback_data="Gramática"),
#             InlineKeyboardButton("Vocabulario básico", callback_data="Vocabulario básico"),
#         ],
#         [
#             InlineKeyboardButton("Práctica", callback_data="Práctica"),
#             InlineKeyboardButton("Recursos adicionales", callback_data="Recursos adicionales"),
#         ],
#         [InlineKeyboardButton("Done", callback_data="Done")],
#     ]

#     reply_markup = InlineKeyboardMarkup(keyboard)

#     # Actualizar el mensaje
#     await update.callback_query.edit_message_text(
#         text=f"La palabra que seleccionaste se traduce como: {translated_text.text}\n\n¿En qué más puedo ayudarte?",
#         reply_markup=reply_markup
#     )

#     # Retornar al menú principal
#     return CHOOSING



# async def options(update, context: ContextTypes.DEFAULT_TYPE):
#     # Crear un objeto Translator
#     translator = Translator()
#     # Traducir un texto al inglés
#     if update.message:
#         query = update.message.callback_query
#         await query.answer()
#         option_selected = query.data
#     elif update.callback_query:
#         query = update.callback_query
#         await query.answer()
#         option_selected = query.data
#     else:
#         return

#     # query = update.callback_query
#     # await query.answer()
#     # option_selected = query.data
#     translated_text = translator.translate(str(option_selected), src="es", dest="en")

#     # await query.edit_message_text(text=f"La palabra que seleccionaste se traduce como: {translated_text.text}")

#      # Editar el mensaje con la traducción
#     await query.edit_message_text(text=f"La palabra que seleccionaste se traduce como: {translated_text.text}")

#     # Retornar al menú principal
#     return await start(update, context)

#     # await query.edit_message_text(
#     #     text=f"La palabra que seleccionaste se traduce como: {translated_text.text}",
#     #     disable_notification=True  # Evita que se muestre automáticamente el mensaje del start
#     # )
    
#     # return CHOOSING



async def gramatica(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("")

    return TYPING_REPLY

async def practica(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aquí hay algunos ejercicios interactivos para que puedas practicar:")
    # Agregar los ejercicios interactivos aquí

async def recursos(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aquí hay algunos recursos adicionales para ayudarte a mejorar tus habilidades en el idioma:")
    # Agregar los recursos adicionales aquí

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data
    if "choice" in user_data:
        del user_data["choice"]

    await update.message.reply_text(
        f"I learned these facts about you: {facts_to_str(user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main():
    dp = Application.builder().token("6055757522:AAEqyK31hZb4ATIs4oeRHnTwlnWjLqQnm-I").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^(Gramática)$"), gramatica),
                MessageHandler(filters.Regex("^(Vocabulario básico)$"), vocabulario),
                MessageHandler(filters.Regex("^(Práctica)$"), practica),
                MessageHandler(filters.Regex("^(Recursos adicionales)$"), recursos),
                MessageHandler(filters.Regex("^(done)$"), done),
            ],
            TYPING_CHOICE: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), vocabulario
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                    practica,
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(options))



    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Correr el bot hasta que se presione Ctrl-C
    dp.run_polling()

if __name__ == "__main__":
    main()
