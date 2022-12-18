import logging
import os

import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Error", status_code=500)
    logging.info(f"Body: {req_body}")
    to_stop = []
    for d in req_body:
        if d["count"] > 3 and d["ConnectionDeviceId"] not in to_stop:
            to_stop.append(d["ConnectionDeviceId"])

    registry_manager = IoTHubRegistryManager(os.environ["ConnectionStr"])
    for device_id in to_stop:
        logging.info(f"Sending emergency stop request for device {device_id}")
        registry_manager.invoke_device_method(device_id, CloudToDeviceMethod(method_name="emergency_stop"))

    return func.HttpResponse("OK", status_code=200)
