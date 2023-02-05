import json
import logging
import os

import functions_framework
import google.cloud.logging
import openai
from flask import Flask, Request, jsonify
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

# Google Cloud Logging クライアント ライブラリを設定
logging_client = google.cloud.logging.Client()
logging_client.setup_logging(log_level=logging.DEBUG)

signing_secret = os.getenv("SLACK_SIGNING_SECRET")
token = os.getenv("SLACK_APP_TOKEN")

# process_before_response must be True when running on FaaS
app = App(token=token, process_before_response=True)

# ここには Flask 固有の記述はありません
# App はフレームワークやランタイムに一切依存しません
@app.command("/hello-bolt")
def hello(body, ack):
    ack(f"Hi <@{body['user_id']}>!")

# Flask アプリを初期化します
flask_app = Flask(__name__)

# SlackRequestHandler は WSGI のリクエストを Bolt のインターフェイスに合った形に変換します
# Bolt レスポンスからの WSGI レスポンスの作成も行います
handler = SlackRequestHandler(app)


@app.event("message")
def message_channel(body, say, logging):
    logging.info(body)


@functions_framework.http
def run(request):
    # handler はアプリのディスパッチメソッドを実行します
    return handler.handle(request)


# @functions_framework.http
# def run(request: Request) -> tuple:
#     """_summary_

#     Args:
#         request (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     headers = {"Content-Type": "application/json"}
#     body = request.get_json()
#     logging.debug(type(body))
#     logging.debug(f"body: {body}")
#     if body.get("type") == "url_verification":
#         res = json.dumps({"challenge": body["challenge"]})
#         logging.debug(f"res: {res}")
#         return (res, 200, headers)
#     elif body.get("type") == "event_callback":
#         user = body["event"]["user"]
#         text = body["event"]["text"]
#         logging.debug(f"user: {user}")
#         logging.debug(f"text: {text}")
#     logging.debug(f"headers: {headers}")
#     return (f"{jsonify({'user': {user}, 'text': {text}})}", 200)


# @app.message("@davinchibot")
# def handle_message(ack, event):
#     """_summary_

#     Args:
#         ack (_type_): _description_
#         event (_type_): _description_
#     """
#     ack("Got your message!")

#     # Use the API Key to create an OpenAI client
#     api_key = os.getenv("OPENAI_API_KEY")
#     openai.api_key = api_key

#     # Use the client to generate a response from ChatGPT
#     response = openai.Completion.create(engine="text-davinci-002", prompt=your_msg)

#     response_msg = response["choices"][0]["text"]

# # '@davinchibot' を含むメッセージをリッスンします
# @app.mention("@davinchibot")
# def send_message(message, say):
#     # イベントがトリガーされたチャンネルへ say() でメッセージを送信します
#     say(
#         blocks=[
#             {
#                 "type": "section",
#                 "text": {"type": "rich_text", "text": f"<@{message['user']}>!"},
#                 "accessory": {
#                     "type": "button",
#                     "text": {"type": "plain_text", "text":"Click Me"},
#                     "action_id": "button_click"
#                 }
#             }
#         ],
#         text=f"Hey there <@{message['user']}>!"
#     )

