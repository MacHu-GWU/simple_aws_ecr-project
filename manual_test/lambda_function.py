# content of lambda_function_1.py

import sys
import json
import s3pathlib

def handler(event, context):
    print(f"event: {json.dumps(event)}")
    response = {
        "message": "Hello from AWS Lambda using Python",
        "sys.version": f"{sys.version}",
        "sys.argv": f"{sys.argv}",
        "s3pathlib version": s3pathlib.__version__,
    }
    print(f"response: {json.dumps(response)}")
    return response
