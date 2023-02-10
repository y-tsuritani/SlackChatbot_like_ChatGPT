import json
from pprint import pprint

import functions_framework
from flask import Flask, Request, jsonify


@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args
    header = request.headers

    print(f"header: {header}")
    pprint(header)

    if header.get("x-slack-retry-num"):
        return jsonify({
            "statusCode": 200,
            "body": json.dumps({"message": "No need to resend"})
        })
    if request_json and "name" in request_json:
        name = request_json["name"]
    elif request_args and "name" in request_args:
        name = request_args["name"]
    else:
        name = "World"
    return "Hello {}!".format(name)
