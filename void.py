import json
import os
from ollama import Client
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters, ConversationHandler

client = Client()
IGNORED_WORDS = {"its", "a", "the", "is", "to", "of"}
DICT_FILE = "void_dictionary.json"

# Load dictionary
if os.path.exists(DICT_FILE):
    with open(DICT_FILE, "r", encoding="utf-8") as f:
        dictionary = json.load(f)
else:
    dictionary = {}

# Store pending questions for each user
pending_questions = {}

def save_dictionary():
    with open(DICT_FILE, "w", encoding="utf-8") as f:
        json.dump(dictionary, f, indent=2)

def extract_meaningful_words(text):
    return [w for w in text.lower().split() if w.isalpha() and w not in IGNORED_WORDS]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or not update.message.from_user:
        return
    
    user_id = update.message.from_user.id
    text = update.message.text.lower()
    
    # Check if user has a pending question
    if user_id in pending_questions:
        word, question = pending_questions[user_id]
        # Store the user's response as the definition
        dictionary[word] = update.message.text.strip()
        save_dictionary()
        await update.message.reply_text(f"Got it! '{word}' means '{update.message.text.strip()}'.")
        del pending_questions[user_id]
        return
    
    words = extract_meaningful_words(text)

    for word in words:
        if word in dictionary:
            continue
        # Ask Gemma to make a question
        prompt = f"Ask a short friendly question to learn what '{word}' means."
        response = client.chat(model="gemma3:1b", messages=[{"role": "user", "content": prompt}])
        question = response['message']['content']
        await update.message.reply_text(question)
        
        # Store the pending question for this user
        pending_questions[user_id] = (word, question)
        break  # Only ask one question at a time

BOT_TOKEN = "7598810333:AAENC7U5X1xRaMHi5mnVz56IPzlGyGJ6zhg"

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()
