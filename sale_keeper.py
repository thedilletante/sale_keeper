from flask import Flask, request
import telepot
import urllib3
import json

with open("config.json") as config:
    jconf = json.load(config)
    if not "secret" in jconf or not "token" in jconf or not "host" in jconf:
        print("There is no valid configuration")
        exit(0)

    secret = jconf["secret"]
    token = jconf["token"]
    host = jconf["host"]
    set_proxy = True

    if "set_proxy" in jconf:
        set_proxy = jconf["set_proxy"]

if set_proxy:
    proxy_url = "http://proxy.server:3128"
    telepot.api._pools = {
        'default': urllib3.ProxyManager(proxy_url=proxy_url,
                                        num_pools=3,
                                        maxsize=10,
                                        retries=False,
                                        timeout=30),
    }
    telepot.api._onetime_pool_spec =\
        (urllib3.ProxyManager,
         dict(proxy_url=proxy_url,
              num_pools=1,
              maxsize=1,
              retries=False,
              timeout=30))

bot = telepot.Bot(token)
bot.setWebhook("{}/{}".format(host, secret), max_connections=1)

app = Flask(__name__)


@app.route('/{}'.format(secret), methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        bot.sendMessage(chat_id, "Ты сказал '{}'".format(text))
    return "OK"
