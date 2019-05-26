import nHentaiTagBot.nHentaiTagBot as hBot
import os
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage
)

app = Flask(__name__)
port = int(os.environ.get('PORT', 33507))

line_bot_api = LineBotApi(
    'Et/GenKz1+jjMORi4d0O3y7gbo6hAxu7QcDhzV2yt+UIEOwTS71OYn1ZaIG'
    'Vl75mwUvmo0jUCBzGDcpZsNYIhU0JPVTSasQR85TY2lqZ9S1j9E2u+Yz'
    'YIIWTFvvhrvzvo73PFli6RDLyPdXokUeLtwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('cf4b093ef93814e87584e46d305357ac')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    m = hBot.processComment(event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=m))


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    print(event.message.originalContentUrl)


app.run(host='0.0.0.0', port=port)

# res = sauce.SauceNow.res(sauce.SauceNow.saucesaucenao("https://img-comment-fun.9cache.com/media/a44pBjA/adxenXgE_700w_0.jpg"))
# res = sauce.Trace.extres(sauce.Trace.saucetrace("https://img-comment-fun.9cache.com/media/a44pBjA/adxenXgE_700w_0.jpg"))
# print(json.dumps(res, indent=4, sort_keys=True))

# res = sauce.Trace.res("https://img-comment-fun.9cache.com/media/a44pBjA/adxenXgE_700w_0.jpg", mode='ext')
# res = sauce.SauceNow.res("https://img-comment-fun.9cache.com/media/a44pBjA/adxenXgE_700w_0.jpg", mode='mini')
# print(res)
