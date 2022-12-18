import asyncio
import datetime
import json
import time
from enum import Enum

from device import Device, DeviceProperty, DeviceMethod
from asyncua import ua
from azure.iot.device import IoTHubDeviceClient, Message, MethodRequest, MethodResponse


class MessageType(Enum):
    TELEMETRY = "telemetry"
    EVENT = "event"


class Agent:
    def __init__(self, device: Device, connection_str: str):
        self.device = device
        self.tasks = []
        self.connection_str = connection_str
        self.client = IoTHubDeviceClient.create_from_connection_string(connection_str)
        self.client.connect()
        self.client.on_method_request_received = self.method_handler
        self.client.on_twin_desired_properties_patch_received = self.twin_update
        self.msg_idx = 0
        self.last_telemetry_date = time.time()
        print(f"Started agent for device {self.device.name}")

    def get_tasks(self):
        tasks = [asyncio.create_task(task) for task in self.tasks]
        self.tasks.clear()
        tasks.append(asyncio.create_task(self.telemetry()))
        return tasks

    async def telemetry(self):
        if self.last_telemetry_date + 1 > time.time():
            return
        self.last_telemetry_date = time.time()
        data = {
            "ProductionStatus": await self.device.read_value(DeviceProperty.ProductionStatus),
            "WorkorderId": await self.device.read_value(DeviceProperty.WorkorderId),
            "GoodCount": await self.device.read_value(DeviceProperty.GoodCount),
            "BadCount": await self.device.read_value(DeviceProperty.BadCount),
            "Temperature": await self.device.read_value(DeviceProperty.Temperature),
        }
        self.send_message(data, MessageType.TELEMETRY)

    @staticmethod
    def get_observed_properties():
        return [
            DeviceProperty.DeviceError,
            DeviceProperty.ProductionRate
        ]

    # handler for device change
    async def datachange_notification(self, node, val, data):
        name = await node.read_browse_name()
        print(f"{name.Name}: {val}")
        if name.Name == DeviceProperty.DeviceError.value:
            patch = {"error": val}
            if val > 0:
                patch["last_error_date"] = datetime.datetime.now().isoformat()
                self.send_message({"error": val}, MessageType.EVENT)
            self.client.patch_twin_reported_properties(patch)
        elif name.Name == DeviceProperty.ProductionRate.value:
            self.client.patch_twin_reported_properties({"production_rate": val})

    def method_handler(self, method: MethodRequest):
        print(f"Received method call on device {self.device.name}")
        if method.name == "emergency_stop":
            self.tasks.append(self.device.call_method(DeviceMethod.EmergencyStop))
        elif method.name == "reset_error_status":
            self.tasks.append(self.device.call_method(DeviceMethod.ResetErrorStatus))
        elif method.name == "maintenance_done":
            self.client.patch_twin_reported_properties({"last_maintenance_date": datetime.datetime.now().isoformat()})
        self.client.send_method_response(MethodResponse(method.request_id, 0))

    def twin_update(self, data):
        print(f"Received twin update on device {self.device.name}: {data}")
        if "production_rate" in data:
            self.tasks.append(self.device.write_value(DeviceProperty.ProductionRate,
                                                      ua.Variant(data["production_rate"], ua.VariantType.Int32)))

    def close(self):
        self.client.shutdown()

    def send_message(self, data, msg_type: MessageType):
        msg = Message(json.dumps(data), f"{self.msg_idx}", "UTF-8", "JSON")
        msg.custom_properties["type"] = msg_type.value
        self.msg_idx += 1
        self.client.send_message(msg)
