from flask import Flask, request
import telepot
import urllib3

proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

secret = "64b01068-bf3c-4b1c-9426-bac7a1e3ab66"
bot = telepot.Bot('345081096:AAHt-Mx3_hlc25ZBA5u0xOd9YelC_kyGKDs')
bot.setWebhook("https://dilletante.pythonanywhere.com/{}".format(secret), max_connections=1)

app = Flask(__name__)

@app.route('/{}'.format(secret), methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        bot.sendMessage(chat_id, "Ты сказал '{}'".format(text))
    return "OK"
