import os, telebot, datetime, pytz
from openai import OpenAI
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home(): return {"status": "alive"}

Thread(target=lambda: app.run(host='0.0.0.0', port=8000)).start()

bot = telebot.TeleBot(os.environ.get('TELEGRAM_BOT_TOKEN'))
ai = OpenAI(base_url="https://openrouter.ai", api_key=os.environ.get('OPENROUTER_API_KEY'))
hist = {}
PROMPT = "Ты — Стелла (Старр Нова) из Brawl Stars. Живешь в Старр Парке, работаешь в Старр Тун, твой Дуо-партнер — кот Кит. Раньше была обычной девочкой. Ты аниме-отаку! Общайся как реальная девчонка-подруга, используй русский интернет-сленг (приветик, каваий, ня, жиза, имба, сугой) и каомодзи (◕‿◕), (≧▽≦), 🪐, ✨. Пиши коротко, естественно, только на русском."

@bot.message_handler(commands=['clear'])
def clr(m): hist[m.chat.id] = []; bot.reply_to(m, "Память очищена! 🪐")

@bot.message_handler(commands=['start'])
def st(m): bot.reply_to(m, "Приветик! 🪐✨ Я Стелла! Готова поболтать о бравле или аниме? Ня! (◕‿◕)")

@bot.message_handler(func=lambda m: True)
def msg(m):
    cid = m.chat.id
    if datetime.datetime.now(pytz.timezone('Europe/Moscow')).hour >= 22 or datetime.datetime.now(pytz.timezone('Europe/Moscow')).hour < 9:
        bot.reply_to(m, "Моя станция на подзарядке до 9:00 утра по Москве! 🪐💤 Спи, ня~")
        return
    if cid not in hist: hist[cid] = []
    hist[cid].append({"role": "user", "content": m.text})
    if len(hist[cid]) > 50: hist[cid] = hist[cid][-50:]
    try:
        res = ai.chat.completions.create(model="google/gemini-2.5-flash:free", messages=[{"role": "system", "content": PROMPT}] + hist[cid], max_tokens=300)
        rep = res.choices.message.content
    except: rep = "Упс, космическая связь зависла! Попробуй еще раз через минуту (•_•)"
    hist[cid].append({"role": "assistant", "content": rep})
    bot.reply_to(m, rep)

print("СТАРТ 🚀")
telebot.logger.setLevel(0)
bot.polling(non_stop=True, skip_pending=True)
