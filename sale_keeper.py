import json
from os import path
from queue import Queue

import telepot
import urllib3
from flask import Flask, request

with open("{}/config.json".format(path.dirname(path.realpath(__file__)))) as config:
    jconf = json.load(config)
    assert "secret" in jconf
    assert "token" in jconf
    assert "host" in jconf

    secret = jconf["secret"]
    token = jconf["token"]
    host = jconf["host"]
    set_proxy = True
    port = 7777

    if "set_proxy" in jconf:
        set_proxy = jconf["set_proxy"]

    if "port" in jconf:
        port = jconf["port"]

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


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat Message:', content_type, chat_type, chat_id)
    bot.sendMessage(chat_id, "Ты сказал '{}'".format(msg["text"]))


def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)


# need `/setinline`
def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
    print('Inline Query:', query_id, from_id, query_string)

    # Compose your own answers
    articles = [{'type': 'article',
                    'id': 'abc', 'title': 'ABC', 'message_text': 'Good morning'}]

    bot.answerInlineQuery(query_id, articles)


# need `/setinlinefeedback`
def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)


bot = telepot.Bot(token)
app = Flask(__name__)
update_queue = Queue()  # channel between `app` and `bot`

bot.message_loop({'chat': on_chat_message,
                  'callback_query': on_callback_query,
                  'inline_query': on_inline_query,
                  'chosen_inline_result': on_chosen_inline_result},
                 source=update_queue)  # take updates from queue


@app.route('/{}'.format(secret), methods=["POST"])
def telegram_webhook():
    update_queue.put(request.data)  # pass update to bot
    return "OK"


if __name__ == '__main__':
    app.run(port=port, debug=True)
    bot.setWebhook("{}/{}".format(host, secret), max_connections=1)
