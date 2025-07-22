import pandas as pd
import openai
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === Hardcoded API keys ===
BOT_TOKEN = "7690348753:AAGmEIzr0vMjlv1NybXK3kbu-XMm3SXDGx0"
OPENROUTER_API_KEY = "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"

# === Load CRM data ===
df = pd.read_csv("crm_data.csv")

def build_context(df):
    return "\n".join([
        f"{r['Client Name']} | {r['Email']} | {r['Phone']} | {r['Order No']} | {r['Order Status']} | {r['Ready Date']}"
        for _, r in df.iterrows()
    ])

crm_context = build_context(df)

# === OpenRouter configuration ===
openai.api_key = OPENROUTER_API_KEY
openai.base_url = "https://openrouter.ai/api/v1"

# === Ask Kimi K2 through OpenRouter ===
def ask_kimi_k2(question: str) -> str:
    prompt = f"""You are a helpful assistant. Based on this CRM data:
{crm_context}

Answer the question: {question}
"""
    try:
        response = openai.chat.completions.create(
            model="moonshotai/kimi-k2",
            messages=[
                {"role": "user", "content": prompt}
            ],
            extra_headers={
                "HTTP-Referer": "https://yourdomain.com",
                "X-Title": "telegram-kimi-bot"
            }
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI API error: {str(e)}"

# === Telegram bot logic ===
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    await update.message.reply_text("⏳ Thinking...")
    try:
        answer = ask_kimi_k2(question)
    except Exception as e:
        answer = f"❌ Error: {e}"
    await update.message.reply_text(answer)

# === Start Telegram bot ===
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# === Optional dummy server to keep Render port alive ===
def run_dummy_server():
    with socketserver.TCPServer(("", 8080), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

print("✅ Telegram bot with Kimi K2 via OpenRouter is running.")
app.run_polling()
