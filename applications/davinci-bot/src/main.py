import json
import logging
import os
import re

import functions_framework
import google.cloud.logging
import openai
from box import Box
from slack_bolt import App, context
from slack_bolt.adapter.google_cloud_functions import SlackRequestHandler
from flask import Request

# Google Cloud Logging クライアント ライブラリを設定
logging_client = google.cloud.logging.Client()
logging_client.setup_logging(log_level=logging.DEBUG)

# 環境変数からシークレットを取得
slack_token = os.environ.get("SLACK_BOT_TOKEN")
openai_api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = openai_api_key

# process_before_response must be True when running on FaaS
app = App(token=slack_token, process_before_response=True)
handler = SlackRequestHandler(app)


# アプリにメンションしたイベントに対する応答
@app.event("app_mention")
def handle_app_mention_events(body: dict, say: context.say.say.Say):
    """アプリへのメンションに対する応答を生成する関数

    Args:
        body: HTTP リクエストのボディ
        say: _description_
    """
    logging.debug(type(body))
    logging.debug(body)
    box = Box(body)
    user = box.event.user
    text = box.event.text
    only_text = re.sub("<@[a-zA-Z0-9]{11}>", "", text)
    logging.debug(only_text)

    # OpenAI から AIモデルの回答を生成する
    openai_response, total_tokens = create_completion(only_text)
    logging.debug(openai_response)
    logging.debug(f"total_tokens: {total_tokens}")

    say(f"<@{user}> {openai_response}\n消費されたトークン:{total_tokens}")


def create_completion(text: str) -> str:
    """OpenAI API を呼び出して、質問に対する回答を生成する関数

    Args:
        text: bot アプリに対する質問内容

    Returns:
        GPT-3 の生成した回答内容
    """
    # openai の GPT-3 モデルを使って、応答を生成する
    response = openai.Completion.create(
        engine="text-davinci-003",  # text-davinci-003 を指定すると最も自然な文章が生成されます
        prompt=text,
        max_tokens=1024,  # 生成する応答の長さ 大きいと詳細な回答が得られますが、多くのトークンを消費します
        temperature=0.5,  # 生成する応答の多様性
        n=1,
        stop=None,
        echo=False
    )
    openai_response = response['choices'][0]['text']
    total_tokens = response['usage']['total_tokens']
    # 応答のテキスト部分を取り出して返す
    return openai_response, total_tokens


@functions_framework.http
def slack_bot(request: Request) -> SlackRequestHandler:
    """slack のイベントリクエストを受信して各処理を実行する関数

    Args:
        request: Slack のイベントリクエスト

    Returns:
        SlackRequestHandler への接続
    """
    header = request.headers
    logging.debug(f"header: {header}")
    body = request.get_json()
    logging.debug(f"body: {body}")

    # URL確認を通すとき
    if body.get("type") == "url_verification":
        logging.info("url verification started")
        headers = {"Content-Type": "application/json"}
        res = json.dumps({"challenge": body["challenge"]})
        logging.debug(f"res: {res}")
        return (res, 200, headers)
    # 応答が遅いと Slack からリトライを何度も受信してしまうため、リトライ時は処理しない
    elif header.get("x-slack-retry-num"):
        logging.info("slack retry received")
        return {"statusCode": 200, "body": json.dumps({"message": "No need to resend"})}

    # handler への接続
    return handler.handle(request)
