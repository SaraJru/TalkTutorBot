from typing import Dict
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
import logging
from telegram.ext import (CommandHandler, MessageHandler, filters,  Application,
                           ContextTypes, ConversationHandler, CallbackQueryHandler, CallbackContext)
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
            InlineKeyboardButton("Buenos días", callback_data="Buenos días"),
            InlineKeyboardButton("Disculpa", callback_data="Disculpa"),
            InlineKeyboardButton("¡Genial!", callback_data="¡Genial!"),
        ],
        [InlineKeyboardButton("¿Qué hora es?", callback_data="¿Qué hora es?")],
        [InlineKeyboardButton("¿En qué puedo ayudarte?", callback_data="¿En qué puedo ayudarte?")],
        [InlineKeyboardButton("Inteligencia artificial", callback_data="Inteligencia artificial")],
        [InlineKeyboardButton("¿Podrías repetir eso, por favor?", callback_data="¿Podrías repetir eso, por favor?")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Empecemos. ¿Qué palabra te gustaría aprender hoy? Puedes escribir la palabra o seleccionarla de la lista:"
        ,reply_markup = reply_markup)


async def vocabulario_options(update, context):
    query = update.callback_query
    await query.answer()
    option_selected = query.data

    # Llamar a la función "selected_option" para manejar la selección del usuario
    next_state = await vocabulario_selected_option(update, context, option_selected)

    return next_state

def traductor(option):
    # Crear un objeto Translator
    translator = Translator()

    # Traducir el texto al inglés
    translated_text = translator.translate(str(option), src="es", dest="en")
    
    return translated_text

async def vocabulario_selected_option(update, context, option_selected):
    
    #Invocamos método para traducir:
    translated_text = traductor(option_selected)
    
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


async def gramatica(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(text="Uso de verbos regulares e irregulares", callback_data="verbos")],
        [InlineKeyboardButton(text="Uso de adjetivos", callback_data="adjetivos")],
        [InlineKeyboardButton(text="Uso de pronombres", callback_data="pronombres")],
        [InlineKeyboardButton(text="Uso de preposiciones", callback_data="preposiciones")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Seleccione una opción para conocer más acerca de la gramática:", reply_markup=reply_markup)


async def gramatica_options(update, context):
    query = update.callback_query
    await query.answer()
    option_selected = query.data

    # Llamar a la función "selected_option" para manejar la selección del usuario
    next_state = await gramatica_selected_option(update, context, option_selected)

    return next_state

async def gramatica_selected_option(update, context, option_selected):
    text = "Retornando"
    if option_selected == "verbos":
        text = "Los verbos en inglés se utilizan para expresar acciones, estados o procesos. Hay dos tipos de verbos: regulares e irregulares. Los verbos regulares forman el pasado y participio pasado añadiendo -ed al infinitivo, mientras que los verbos irregulares tienen formas especiales que no siguen este patrón. Algunos ejemplos de verbos regulares son walked (caminó), talked (habló), played (jugó), mientras que algunos ejemplos de verbos irregulares son go (ir), eat (comer), swim (nadar)."
    elif option_selected == "adjetivos":
        text = "Los adjetivos en inglés se utilizan para describir o calificar a los sustantivos. Normalmente, los adjetivos se colocan antes del sustantivo que modifican. Algunos ejemplos de adjetivos en inglés son happy (feliz), sad (triste), big (grande), small (pequeño)."
    elif option_selected == "pronombres":
        text = "Los pronombres en inglés se utilizan en lugar de los sustantivos para evitar repetir los mismos nombres una y otra vez. Algunos ejemplos de pronombres en inglés son I (yo), you (tú), he (él), she (ella), we (nosotros), they (ellos)."
    elif option_selected == "preposiciones":
        text = "Las preposiciones en inglés se utilizan para establecer relaciones entre sustantivos, pronombres y otras palabras en una oración. Algunos ejemplos de preposiciones en inglés son in (en), on (sobre), under (debajo), above (encima), below (debajo)."
    elif option_selected == "menu":
        # Si se selecciona la opción "Volver al menú principal", se llama a la función start
       if update.callback_query:
        query = update.callback_query
        await query.answer()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Hola! ¿En qué puedo ayudarte?",
            reply_markup=markup
        )
    else:
        # Si se selecciona una opción inválida, mostrar un mensaje de error
        text = "Lo siento, opción inválida. Por favor, selecciona una opción válida."
    # Responder al usuario con el texto en español
    await update.callback_query.edit_message_text(
        text=f"{text}"
    )

    # Enviar el mensaje del menú principal
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        keyboard = [
            [InlineKeyboardButton(text="Uso de verbos regulares e irregulares", callback_data="verbos")],
            [InlineKeyboardButton(text="Uso de adjetivos", callback_data="adjetivos")],
            [InlineKeyboardButton(text="Uso de pronombres", callback_data="pronombres")],
            [InlineKeyboardButton(text="Uso de preposiciones", callback_data="preposiciones")],
            [InlineKeyboardButton(text="Volver al menú principal", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Selecciona una opción:",
            reply_markup=reply_markup
        )
    return CHOOSING

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
    dp = Application.builder().token("").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^(Gramática)$"), gramatica),
                MessageHandler(filters.Regex("^(Vocabulario básico)$"), vocabulario),
                MessageHandler(filters.Regex("^(Práctica)$"), practica),
                MessageHandler(filters.Regex("^(Recursos adicionales)$"), recursos),
                MessageHandler(filters.Regex("^(done)$"), done),
                CallbackQueryHandler(gramatica_options, pattern="^" + "verbos|adjetivos|pronombres|preposiciones|menu" + "$"),
                CallbackQueryHandler(vocabulario_options, pattern="^" + "hola|Buenos días|Disculpa|¡Genial!|¿Qué hora es?|¿En qué puedo ayudarte?|Inteligencia artificial|¿Podrías repetir eso, por favor?" + "$"),
            ],
            TYPING_CHOICE: [
                
            ],
            TYPING_REPLY: [
            
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )

    dp.add_handler(conv_handler)

    dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Correr el bot hasta que se presione Ctrl-C
    dp.run_polling()

if __name__ == "__main__":
    main()
