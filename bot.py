import os
import telebot
from dotenv import load_dotenv
import threading
import time
from translate import Translator  # Import the Translator class from the translate library
import single_LLM 
import multi_LLM 
import json
import multi_context

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
bot.set_webhook()

# Language options
languages = {
    "English": "en",
    "Tamil": "ta",
    "Chinese": "zh-CN",
    "Malay": "ms",
    "Bangla": "bn",
    "Burmese": "my", 
}

# Create a dictionary to store the selected language for each user
user_languages = {}

# Create a dictionary to store the user's questions in their chosen language
user_questions = {}

# Maximum number of characters for translation per query
MAX_TRANSLATION_CHARACTERS = 500

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.from_user.id
        # Check if the user has a selected language stored
        if user_id in user_languages:
            selected_language = user_languages[user_id]
            start_message = f"Welcome back! You're currently using {selected_language}. You can change the language by typing /reset."
        else:
            # Start bot introduction
            start_message = "Hello! My name is Jamie, and I am your friendly AI powered chatbot. I am here to help you with all matters related to MOM's Settling-in Programme (SIP). Topics I am well versed with include: \n\n- Singapore's social norms \n- Employment rights and responsibilities \n- Singapore laws \n- Where and how to seek assistance \n\nPlease choose the language for translation at the start:"
        
            # Create a custom keyboard with language options
            markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
            for language in languages:
                markup.add(telebot.types.KeyboardButton(language))
            
            start_message += "\n(You can also type /reset to choose a different language at any time.)"
            bot.send_message(message.chat.id, start_message, reply_markup=markup)

    except Exception as e:
        bot.send_message(
            message.chat.id, 'Sorry, something seems to have gone wrong! Please try again later.')

@bot.message_handler(func=lambda message: message.text in languages)
def handle_language_selection(message):
    try:
        # Store the selected language for the user
        user_id = message.from_user.id
        selected_language = languages[message.text]
        user_languages[user_id] = selected_language

        # Ask the user to enter their question in the chosen language
        bot.send_message(message.chat.id, "Great choice! Please enter your question in this language:")

    except Exception as e:
        bot.send_message(
            message.chat.id, 'Sorry, something seems to have gone wrong! Please try again later.')

def translate_text(text, dest_language):
    translator = Translator(to_lang=dest_language)
    translated_text = ""
    for i in range(0, len(text), MAX_TRANSLATION_CHARACTERS):
        chunk = text[i:i + MAX_TRANSLATION_CHARACTERS]
        translated_chunk = translator.translate(chunk)
        translated_text += translated_chunk
    # translated_text += translator.translate("\nYou can ask the next question! ")
    return translated_text

@bot.message_handler(commands=['reset'])
def reset_language(message):
    user_id = message.from_user.id
    # Remove the user's selected language
    if user_id in user_languages:
        del user_languages[user_id]
    bot.send_message(message.chat.id, "Language reset. Please choose a language.")

def show_typing_indicator(chat_id, stop_event):
    while not stop_event.is_set():
        bot.send_chat_action(chat_id=chat_id, action='typing')
        time.sleep(2)

@bot.message_handler(content_types=['text'])
def send_text(message):
    user_id = message.from_user.id

    stop_typing_event = threading.Event()
    
    typing_thread = threading.Thread(target=show_typing_indicator, args=(message.chat.id, stop_typing_event))
    typing_thread.start()
 
    if user_id in user_languages:
        # Get the selected language (short form) for the user
        selected_language = user_languages[user_id]

        # Store the user's question in their chosen language
        user_questions[user_id] = {
            "language": selected_language,
            "question": message.text
        }

        # Translate the question to English to query your model
        if selected_language != "en":
            english_question = translate_text(message.text, "en")
        else:
            english_question = message.text

        # Get the response in English
        # response = single_LLM.getResponse(english_question) ############ UNCOMMENT FOR SINGLE LLM
        # response = multi_LLM.getResponse(english_question) ############ UNCOMMENT FOR MULTI LLM
        response = multi_context.getResponse(english_question) ############ UNCOMMENT FOR MULTI CONTEXT
        english_response = response["answer"]
        source_documents = response["source_documents"]

        # Extract sources from source_documents
        sources = set()
        for doc in source_documents:
            source = doc.metadata.get('source', 'Unknown Source')
            splitted_source = source.split("/")
            source = splitted_source[-1]
            page_number = doc.metadata.get('page', 'No Page')
            if source not in sources:
                sources.add((source, page_number))

        # Prepare the sources list
        sources_text = ""
        for idx, (source, page) in enumerate(sources, 1):
            sources_text += f"{idx}. {source} - Page {page}\n"

        # Get the full name of the selected language
        full_language_name = next((k for k, v in languages.items() if v == selected_language), selected_language)

        # Send the English question and answer
        #bot.send_message(message.chat.id, f"Your Question ({full_language_name}):\n{message.text}")
        
        # Translate the English answer to the selected language
        translated_response = translate_text(english_response, selected_language)
        translated_sources = translate_text(sources_text, selected_language)
        
        stop_typing_event.set()
        typing_thread.join()

        # Send the answer and sources in the selected language
        bot.send_message(
            message.chat.id, 
            f"*{full_language_name} Answer:*\n{translated_response}\n\n*{translate_text('References', selected_language)}:*\n{translated_sources}",
            parse_mode="Markdown"
        )


def main():
    print('Loading configuration...')
    print('Successfully loaded! Starting bot...')
    bot.infinity_polling()

if __name__ == '__main__':
    main()
