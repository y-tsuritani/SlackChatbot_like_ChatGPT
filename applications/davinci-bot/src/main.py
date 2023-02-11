import json
import logging
import os
import re

import functions_framework
import google.cloud.logging
import openai
from box import Box
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

# Google Cloud Logging クライアント ライブラリを設定
logging_client = google.cloud.logging.Client()
logging_client.setup_logging(log_level=logging.DEBUG)

# 環境変数からシークレットを取得
slack_token = os.environ.get("SLACK_BOT_TOKEN")
openai_api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = openai_api_key

# process_before_response must be True when running on FaaS
app = App(process_before_response=True)
handler = SlackRequestHandler(app)


# アプリにメンションしたイベントに対する応答
@app.event("app_mention")
def handle_app_mention_events(body, say, logger):
    """_summary_

    Args:
        body (_type_): _description_
        say (_type_): _description_
        logger (_type_): _description_
    """
    logger.info(body)
    box = Box(body)
    user = box.event.user
    logging.debug(user)
    text = box.event.text
    logging.debug(text)
    only_text = re.sub("<@[a-zA-Z0-9]{11}>", "", text)
    logging.debug(only_text)

    # OpenAI から AIモデルの回答を生成する
    openai_response, total_tokens = create_completion(only_text)
    logging.debug(openai_response)
    logging.debug(f"total_tokens: {total_tokens}")

    say(f"<@{user}>{openai_response}\n消費されたトークン:{total_tokens}")


def create_completion(text: str) -> str:
    """_summary_

    Args:
        text (str): _description_

    Returns:
        str: _description_
    """
    # openai の GPT-3 モデルを使って、応答を生成する
    response = openai.Completion.create(
        engine="text-davinci-003", # text-davinci-003 を指定すると最も自然な文章が生成されます
        prompt=text,
        max_tokens=256,  # 生成する応答の長さ 大きいと詳細な回答が得られますが、多くのトークンを消費します
        temperature=0.5, # 生成する応答の多様性
        n=1,
        stop=None,
        echo=False
    )
    openai_response = response['choices'][0]['text']
    total_tokens = response['usage']['total_tokens']
    # 応答のテキスト部分を取り出して返す
    return openai_response, total_tokens


@functions_framework.http
def slack_bot(request):
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
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

    # handler を呼び出す
    return handler.handle(request)