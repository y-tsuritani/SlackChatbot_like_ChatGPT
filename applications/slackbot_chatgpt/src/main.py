import json
import logging
import os

import functions_framework
import google.cloud.logging
import openai
from flask import Request, jsonify
from slack_bolt import App

# Google Cloud Logging クライアント ライブラリを設定
logging_client = google.cloud.logging.Client()
logging_client.setup_logging(log_level=logging.DEBUG)

signing_secret = os.getenv("SLACK_SIGNING_SECRET")
token = os.getenv("SLACK_APP_TOKEN")
app = App(token=token)


@functions_framework.http
def verify(request: Request) -> tuple:
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
        json_body = jsonify(body)
        user = json_body.json()["event"]["user"]
        text = json_body.json()["event"]["blocks"]["elements"]["elements"]["text"]
        logging.debug(f"user: {user}")
        logging.debug(f"text: {text}")
    logging.debug(f"headers: {headers}")
    return ("{}", 200, jsonify({'user': user, 'text': text}))


@app.message("hello")
def handle_message(ack, event):
    """_summary_

    Args:
        ack (_type_): _description_
        event (_type_): _description_
    """
    ack("Got your message!")

    # Use the API Key to create an OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key

    # Use the client to generate a response from ChatGPT
    response = openai.Completion.create(engine="text-davinci-002", prompt=your_msg)

    response_msg = response["choices"][0]["text"]


if __name__ == "__main__":
    app.run()
