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

# Use the API Key to create an OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")
signing_secret = os.getenv("SLACK_SIGNING_SECRET")
token = os.getenv("SLACK_APP_TOKEN")

# process_before_response must be True when running on FaaS
app = App(token=token, process_before_response=True)

# SlackRequestHandler は WSGI のリクエストを Bolt のインターフェイスに合った形に変換します
# Bolt レスポンスからの WSGI レスポンスの作成も行います
handler = SlackRequestHandler(app)


@functions_framework.http
def run(request: Request) -> tuple:
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    headers = {"Content-Type": "application/json"}
    body = request.get_json()
    logging.debug(type(body))
    logging.debug(f"body: {body}")
    if body.get("type") == "url_verification":
        res = json.dumps({"challenge": body["challenge"]})
        logging.debug(f"res: {res}")
        return (res, 200, headers)
    elif body.get("type") == "event_callback":
        user = body["event"]["user"]
        text = body["event"]["text"]
        logging.debug(f"user: {user}")
        logging.debug(f"text: {text}")
    logging.debug(f"headers: {headers}")

    # Use the client to generate a response from ChatGPT
    response = openai.Completion.create(engine="text-davinci-002", prompt=text)
    response_msg = response["choices"][0]["text"]
    logging.info(f"response: {response_msg}")
    return (response_msg, 200)

