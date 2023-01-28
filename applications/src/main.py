import os

import functions.framework
import openai
from slack_bolt import App

token = "xoxb-3470110323764-4706232038646-5ciLXItAcC1Ylft8RQHffEeh"
# token = os.getenv()
app = App(token=token)


@functions_framework.http
def run(request):
    pass
    return None


@app.message("hello")
def handle_message(ack, event):
    ack("Got your message!")

    # Use the API Key to create an OpenAI client
    api_key = "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"
    # api_key = os.getenv()
    openai.api_key = api_key

    # Use the client to generate a response from ChatGPT
    response = openai.Completion.create(engine="text-davinci-002", prompt=your_msg)

    response_msg = response["choices"][0]["text"]


if __name__ == "__main__":
    app.run()
