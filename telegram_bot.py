# === File: telegram_bot.py ===
import pandas as pd
import os
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from openai import OpenAI

# === Secrets ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "7690348753:AAGmEIzr0vMjlv1NybXK3kbu-XMm3SXDGx0")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

# === Load CSV ===
df = pd.read_csv("crm_data.csv")

def build_context(df):
    return "\n".join([
        f"{r['Client Name']} | {r['Email']} | {r['Phone']} | {r['Order No']} | {r['Order Status']} | {r['Ready Date']}"
        for _, r in df.iterrows()
    ])

crm_context = build_context(df)

# === OpenRouter Client ===
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def ask_kimi_k2(question: str) -> str:
    prompt = f"""You are a helpful assistant. Based on this CRM data:
{crm_context}

Answer the question: {question}
"""
    try:
        response = client.chat.completions.create(
            model="moonshotai/kimi-k2",
            messages=[{"role": "user", "content": prompt}],
            timeout=20,  # ⏱ Limit
            extra_headers={
                "HTTP-Referer": "https://yourdomain.com",
                "X-Title": "telegram-kimi-bot"
            },
        )
        return response.choices[0].message.content
    except httpx.ReadTimeout:
        return "⚠️ Timeout: Kimi API took too long to respond."
    except Exception as e:
        return f"❌ Error: {e}"

# === Telegram Handler ===
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    await update.message.reply_text("⏳ Thinking...")
    answer = ask_kimi_k2(question)
    await update.message.reply_text(answer)

# === Start App ===
if __name__ == "__main__":
    print("✅ Telegram bot with Kimi K2 is starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.run_polling()
