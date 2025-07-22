from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from langchain.agents import create_pandas_dataframe_agent
from langchain.llms import OpenAI
import pandas as pd

# === CONFIG ===
BOT_TOKEN = "7690348753:AAGmEIzr0vMjlv1NybXK3kbu-XMm3SXDGx0"
OPENAI_API_KEY = "PASTE_YOUR_OPENAI_API_KEY_HERE"
CSV_FILE = "crm_data.csv"

# === Load Data and Agent ===
df = pd.read_csv(CSV_FILE)
llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
agent = create_pandas_dataframe_agent(llm, df, verbose=False)

# === Telegram Bot Logic ===
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    print(f"User asked: {question}")
    try:
        answer = agent.run(question)
    except Exception as e:
        answer = f"❌ Error: {e}"
    await update.message.reply_text(answer)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
print("✅ Bot with AI agent is running...")
app.run_polling()
