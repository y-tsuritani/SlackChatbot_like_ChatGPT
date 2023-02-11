import json
import logging
import os

import functions_framework
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from box import Box

logging.basicConfig(level=logging.DEBUG)

slack_token = os.environ.get("SLACK_BOT_TOKEN")
openai_api_key = os.environ.get("OPENAI_API_KEY")

# process_before_response must be True when running on FaaS
app = App(process_before_response=True)
handler = SlackRequestHandler(app)


@app.event("message")
def message_channel(body, say, logger):
    logger.info(body)
    box = Box(body)
    say(box.event.text)

@app.event("app_mention")
def handle_app_mention_events(body, say, logger):
    logger.info(body)
    box = Box(body)
    say(box.event.text)



@functions_framework.http
def echo_bot(request):
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
    # 応答が遅いとSlackからリトライを受信してしまうため、リトライ時は処理しない
    elif header.get("x-slack-retry-num"):
        logging.info("slack retry received")
        return {"statusCode": 200, "body": json.dumps({"message": "No need to resend"})}

    return handler.handle(request)
