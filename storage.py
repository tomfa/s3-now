import json


def json_request(event, context):
    method = event.httpMethod
    parameters = event.queryStringParameters
    authorization = event.headers.Authorization

    body = {
        "message": "s3-now to the rescue!",
        "method": method,
        "parameters": parameters,
        "authorization": authorization,
        "input": event,
    }

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response
