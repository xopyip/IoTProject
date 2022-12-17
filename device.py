from enum import Enum
from asyncua import Client, ua


class DeviceProperty(Enum):
    ProductionStatus = "ProductionStatus"
    WorkorderId = "WorkorderId"
    ProductionRate = "ProductionRate"
    GoodCount = "GoodCount"
    BadCount = "BadCount"
    Temperature = "Temperature"
    DeviceError = "DeviceError"


class DeviceMethod(Enum):
    EmergencyStop = "EmergencyStop"
    ResetErrorStatus = "ResetErrorStatus"


class Device:

    def __init__(self, client: Client, id):
        self.entries = {}
        self.id = id
        self.name = "Unknown"
        self.client = client

    @classmethod
    async def create(cls, client: Client, id):
        self = Device(client, id)
        device = client.get_node(id)
        self.name = (await device.read_browse_name()).Name
        children = await device.get_children()
        for child in children:
            node = client.get_node(child)
            node_name = await node.read_browse_name()
            self.entries[node_name.Name] = child
        return self

    async def read_value(self, prop: DeviceProperty):
        return await self.get_node(prop).read_value()

    async def call_method(self, prop: DeviceMethod):
        node = self.client.get_node(self.id)
        await node.call_method(prop.value)

    def get_node(self, prop: DeviceProperty):
        return self.client.get_node(self.entries[prop.value])

    async def write_value(self, prop: DeviceProperty, val: ua.Variant):
        node = self.get_node(prop)
        await node.write_value(val)


class Factory:
    def __init__(self, client):
        self.devices = []
        self.client = client

    @classmethod
    async def create(cls, client: Client):
        self = Factory(client)
        objects = self.client.get_node(client.nodes.objects)  # objects node
        for child in await objects.get_children():
            child_name = await child.read_browse_name()
            if child_name.Name != "Server":
                self.devices.append(await Device.create(self.client, child))
        return self

    async def list_devices(self, extended=False):
        for device in self.devices:
            print(device.name)
            if extended:
                for prop in DeviceProperty:
                    print(f"  - {prop.name}: {await device.read_value(prop)}")
