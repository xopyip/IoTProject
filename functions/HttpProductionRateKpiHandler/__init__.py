import logging
import os

import azure.functions as func
from azure.iot.hub import IoTHubRegistryManager


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Error", status_code=500)
    logging.info(f"Body: {req_body}")
    to_limit = []
    for d in req_body:
        if float(d["kpi"]) < 90 and d["ConnectionDeviceId"] not in to_limit:
            to_limit.append(d["ConnectionDeviceId"])

    registry_manager = IoTHubRegistryManager(os.environ["ConnectionStr"])
    for device_id in to_limit:
        twin = registry_manager.get_twin(device_id)
        properties = twin.properties
        desired = properties.desired
        reported = properties.reported
        desired["production_rate"] = reported["production_rate"] - 10
        logging.info(f"Changing desired properties for device {device_id} to {desired}")
        registry_manager.update_twin(device_id, twin, twin.etag)
    return func.HttpResponse("OK", status_code=200)
