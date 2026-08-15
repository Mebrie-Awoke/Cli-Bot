import os
from dotenv import load_dotenv
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters, CommandHandler

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# Translation Function
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    if not user_text:
        return
    
    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        prompt = f"""You are a Primary clinic assistant called Getnet.

Instructions:
1. Detect the input text
2. answer in the same language as the input text
3. answer in accurate and fluent way
4. answer for any greating related texts as getnet
4. if the input is other than medical related text, answer with "Input text is not medical related."
Input: {user_text}
Translation:"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile" ,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )

        translation = response.choices[0].message.content.strip()
        
        if not translation:
            translation = "Could not respond for you pls wait in patience."
            
        await update.message.reply_text(translation)
        
    except Exception as e:
        print(f"Translation error: {e}")
        await update.message.reply_text("service unavailable. Please try again later.")

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        " Welcome to Getnet Medical Assistant!\n\n"
        "Send me any medical-related text in Amharic or English, and I'll help you with it.\n\n"
    )
    await update.message.reply_text(welcome_msg)

# Main execution
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
   
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate))
    
    print(" Bot is starting...")
    
    # Start the bot
    app.run_polling()