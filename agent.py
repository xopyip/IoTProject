import json

from device import Device, DeviceProperty
from azure.iot.device import IoTHubDeviceClient, Message, MethodRequest, MethodResponse


class Agent:
    def __init__(self, device: Device, connection_str: str):
        self.device = device
        self.connection_str = connection_str
        self.client = IoTHubDeviceClient.create_from_connection_string(connection_str)
        self.client.connect()
        self.client.on_message_received = self.message_handler
        self.client.on_method_request_received = self.method_handler
        self.client.on_twin_desired_properties_patch_received = self.twin_update
        self.msg_idx = 0
        print(f"Started agent for device {self.device.name}")

    async def telemetry(self):
        data = {
            "ProductionStatus": await self.device.read_value(DeviceProperty.ProductionStatus),
            "WorkorderId": await self.device.read_value(DeviceProperty.WorkorderId),
            "GoodCount": await self.device.read_value(DeviceProperty.GoodCount),
            "BadCount": await self.device.read_value(DeviceProperty.BadCount),
            "Temperature": await self.device.read_value(DeviceProperty.Temperature),
        }
        msg = Message(json.dumps(data), f"{self.msg_idx}", "UTF-8", "JSON")
        self.msg_idx += 1
        self.client.send_message(msg)

    def message_handler(self, message):
        print(f"Received message on device {self.device.name}")
        print(message.data)
        print(message.custom_properties)

    def method_handler(self, method: MethodRequest):
        print(f"Received method call on device {self.device.name}")
        print(method.name)
        print(method.payload)
        self.client.send_method_response(MethodResponse(method.request_id, 0))

    def twin_update(self, data):
        print(f"Received twin update on device {self.device.name}")
        print(data)

    def close(self):
        self.client.shutdown()

