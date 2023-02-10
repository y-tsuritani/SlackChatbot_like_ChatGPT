import json
import logging
import os

import functions_framework
import google.cloud.logging
import openai
# import requests
from flask import Flask, jsonify, Request

# Google Cloud Logging クライアント ライブラリを設定
logging_client = google.cloud.logging.Client()
logging_client.setup_logging(log_level=logging.DEBUG)

slack_token = os.environ.get("SLACK_BOT_TOKEN")
openai_api_key = os.environ.get("OPENAI_API_KEY")

openai.api_key = openai_api_key

app = Flask(__name__)


@functions_framework.http
def handler(req: Request) -> dict:
    """_summary_

    Args:
        event (_type_): _description_
        context (_type_): _description_

    Returns:
        _type_: _description_
    """
    header = req.headers()
    body = req.get_json()
    if body.get("type") == "url_verification":
        headers = {"Content-Type": "application/json"}
        res = json.dumps({"challenge": body["challenge"]})
        logging.debug(f"res: {res}")
        return (res, 200, headers)
    elif header.get("x-slack-retry-num"):
        return jsonify({
            "statusCode": 200,
            "body": json.dumps({"message": "No need to resend"})
        })
    body = json.loads(body["body"])
    text = body["event"]["text"].replace("<@.*>", "")

    openai_response = create_completion(text)

    thread_ts = body["event"]["thread_ts"] if "thread_ts" in body["event"] else body["event"]["ts"]
    post_message(body["event"]["channel"], openai_response, thread_ts)

    return jsonify({
        "statusCode": 200,
        "body": json.dumps({"message": openai_response})
    })


def create_completion(text: str) -> str:
    """_summary_

    Args:
        text (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=text,
            temperature=0.5,
            max_tokens=2048,
            n=1,
            stop=None,
            echo=False
        )
        return response["choices"][0]["text"]
    except Exception as err:
        logging.error(err)


def post_message(channel: str, text: str, thread_ts: str) -> None:
    """_summary_

    Args:
        channel (_type_): _description_
        text (_type_): _description_
        thread_ts (_type_): _description_
    """
    try:
        headers = {
            "Authorization": f"Bearer {slack_token}",
            "Content-Type": "application/json;charset=utf-8"
        }
        data = {
            "channel": channel,
            "text": text,
            "as_user": True,
            "thread_ts": thread_ts
        }
        response = requests.post("https://slack.com/api/chat.postMessage", headers=headers, json=data)
        response.raise_for_status()
    except Exception as err:
        logging.error(err)
