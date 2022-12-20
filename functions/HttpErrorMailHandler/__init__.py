import logging
import os

import azure.functions as func
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Error", status_code=500)
    logging.info(f"Body: {req_body}")
    errors = []
    for d in req_body:
        if d["error"] not in errors:
            errors.append(f"<li>{d['error']} @ {d['ConnectionDeviceId']}</li>")

    message = Mail(
        from_email=os.environ["SendGridSender"],
        to_emails=os.environ["SendGridReceiver"],
        subject='IoT Error',
        html_content='<strong>List of errors:</strong><ul>' + ("".join(errors)) + '</ul>')
    try:
        sg = SendGridAPIClient(os.environ["SendGridToken"])
        sg.send(message)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)

    return func.HttpResponse("OK", status_code=200)
