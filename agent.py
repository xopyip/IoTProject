from device import Device
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
        print(f"Started agent for device {self.device.name}")

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

